// customer_scores — model output from python/03_train_score.py (one row per customer)
// Change the path if the project lives somewhere else.
let
    Source = Csv.Document(
        File.Contents("D:\Personal_projects\cross-sell-propensity\data\processed\customer_scores.csv"),
        [Delimiter = ",", Columns = 5, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    // "en-US" culture so 0.173678 is read with a dot decimal whatever the PC's regional settings are.
    // id must be Whole Number to match train_cleaned[id] for the relationship.
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"id", Int64.Type}, {"probability", type number}, {"tier", type text},
        {"split", type text}, {"rank", Int64.Type}
    }, "en-US")
in
    #"Changed Type"
