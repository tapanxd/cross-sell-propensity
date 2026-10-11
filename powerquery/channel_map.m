// channel_map — 155 channel codes -> name and type (synthetic reference table)
let
    Source = Odbc.DataSource("dsn=cross_sell", [HierarchicalNavigation = true]),
    channel_map_Table = Source{[Name = "channel_map", Kind = "Table"]}[Data],

    // Key must be Whole Number to match train_cleaned.Policy_Sales_Channel, or the merge returns nulls
    #"Changed Type" = Table.TransformColumnTypes(channel_map_Table, {
        {"channel_code", Int64.Type},
        {"channel_name", type text}, {"channel_type", type text}
    })
in
    #"Changed Type"
