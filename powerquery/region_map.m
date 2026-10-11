// region_map — 53 region codes -> GTA name, zone, area type (synthetic reference table)
let
    // Connect through the SQLite ODBC DSN set up in Power BI (no username/password: "Default or Custom")
    Source = Odbc.DataSource("dsn=cross_sell", [HierarchicalNavigation = true]),
    region_map_Table = Source{[Name = "region_map", Kind = "Table"]}[Data],

    // ODBC hands every SQLite number over as Decimal; the key must be Whole Number to match train_cleaned
    #"Changed Type" = Table.TransformColumnTypes(region_map_Table, {
        {"region_code", Int64.Type},
        {"region_name", type text}, {"zone", type text}, {"area_type", type text}
    })
in
    #"Changed Type"
