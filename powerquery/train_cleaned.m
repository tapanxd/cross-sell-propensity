// train_cleaned — base customer table, merged with both reference tables, plus 3 engineered columns.
// Exported to data/processed/engineered.csv (via DAX Studio) for the Python model.
let
    Source = Odbc.DataSource("dsn=cross_sell", [HierarchicalNavigation = true]),
    train_cleaned_Table = Source{[Name = "train_cleaned", Kind = "Table"]}[Data],

    // ODBC drops the INTEGER declarations from 02_clean.sql, so re-apply them.
    // Annual_Premium is the only true decimal quantity; codes and 0/1 flags are Whole Number.
    #"Changed Type" = Table.TransformColumnTypes(train_cleaned_Table, {
        {"id", Int64.Type}, {"Age", Int64.Type}, {"Driving_License", Int64.Type},
        {"Region_Code", Int64.Type}, {"Previously_Insured", Int64.Type},
        {"Policy_Sales_Channel", Int64.Type}, {"Vintage", Int64.Type}, {"Response", Int64.Type},
        {"Annual_Premium", type number},
        {"Gender", type text}, {"Vehicle_Age", type text}, {"Vehicle_Damage", type text}
    }),

    // LEFT OUTER: keep every customer even if a code is missing from the reference table.
    // Inner would silently drop them the day a new code appears upstream.
    #"Merged Queries" = Table.NestedJoin(#"Changed Type", {"Region_Code"}, region_map, {"region_code"},
        "region_map", JoinKind.LeftOuter),
    // Expand only the columns the dashboard needs; new names drop the "region_map." prefix
    #"Expanded region_map" = Table.ExpandTableColumn(#"Merged Queries", "region_map",
        {"region_name", "zone", "area_type"}, {"region_name", "zone", "area_type"}),

    #"Merged Queries1" = Table.NestedJoin(#"Expanded region_map", {"Policy_Sales_Channel"}, channel_map, {"channel_code"},
        "channel_map", JoinKind.LeftOuter),
    #"Expanded channel_map" = Table.ExpandTableColumn(#"Merged Queries1", "channel_map",
        {"channel_name", "channel_type"}, {"channel_name", "channel_type"}),

    // Tenure Band (built with the Conditional Column UI). Vintage is flat across 10–299 days,
    // so the cuts are business-meaning ones: first quarter / half year. First matching rule wins.
    #"Added Conditional Column" = Table.AddColumn(#"Expanded channel_map", "Tenure Band", each
        if [Vintage] < 90 then "new"
        else if [Vintage] < 180 then "established"
        else "long-standing"),

    // Premium Band (typed by hand as a Custom Column). 2,630 is a floor shared by 17% of customers,
    // so it is its own band and checked FIRST; 30K / 38K are the rounded terciles of the non-base rows.
    #"Added Custom" = Table.AddColumn(#"Added Conditional Column", "Premium Band", each
        if [Annual_Premium] = 2630 then "base"
        else if [Annual_Premium] < 30000 then "low"
        else if [Annual_Premium] < 38000 then "medium"
        else "high"),

    // Custom/conditional columns come out typed "any"; set Text so profiling and the data model work
    #"Changed Type1" = Table.TransformColumnTypes(#"Added Custom", {
        {"Tenure Band", type text}, {"Premium Band", type text}
    }),

    // Channel Group: top 10 channel codes (92% of customers) by name, the 145-code tail as "Other"
    #"Added Custom1" = Table.AddColumn(#"Changed Type1", "Channel Group", each
        if List.Contains({152, 26, 124, 160, 156, 122, 157, 154, 151, 163}, [Policy_Sales_Channel])
        then [channel_name]
        else "Other"),
    #"Changed Type2" = Table.TransformColumnTypes(#"Added Custom1", {{"Channel Group", type text}})
in
    #"Changed Type2"
