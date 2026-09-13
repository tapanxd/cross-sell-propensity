SELECT 
    COUNT(*) AS total_rows,
    COUNT(id) AS total_non_null_ids,
    COUNT(DISTINCT id) AS unique_id_count,
    CASE 
        WHEN COUNT(*) = COUNT(DISTINCT id) THEN 'Yes - ID is unique'
        ELSE 'No - ID has duplicates'
    END AS is_unique
FROM train;


SELECT
    SUM(CASE WHEN id IS NULL OR id = '' THEN 1 ELSE 0 END) AS id_blank_count,
    SUM(CASE WHEN Gender IS NULL OR Gender = '' THEN 1 ELSE 0 END) AS Gender_blank_count,
    SUM(CASE WHEN Age IS NULL OR Age = '' THEN 1 ELSE 0 END) AS Age_blank_count,
    SUM(CASE WHEN Driving_License IS NULL OR Driving_License = '' THEN 1 ELSE 0 END) AS Driving_License_blank_count,
    SUM(CASE WHEN Region_Code IS NULL OR Region_Code = '' THEN 1 ELSE 0 END) AS Region_Code_blank_count,
    SUM(CASE WHEN Previously_Insured IS NULL OR Previously_Insured = '' THEN 1 ELSE 0 END) AS Previously_Insured_blank_count,
    SUM(CASE WHEN Vehicle_Age IS NULL OR Vehicle_Age = '' THEN 1 ELSE 0 END) AS Vehicle_Age_blank_count,
    SUM(CASE WHEN Vehicle_Damage IS NULL OR Vehicle_Damage = '' THEN 1 ELSE 0 END) AS Vehicle_Damage_blank_count,
    SUM(CASE WHEN Annual_Premium IS NULL OR Annual_Premium = '' THEN 1 ELSE 0 END) AS Annual_Premium_blank_count,
    SUM(CASE WHEN Policy_Sales_Channel IS NULL OR Policy_Sales_Channel = '' THEN 1 ELSE 0 END) AS Policy_Sales_Channel_blank_count,
    SUM(CASE WHEN Vintage IS NULL OR Vintage = '' THEN 1 ELSE 0 END) AS Vintage_blank_count,
    SUM(CASE WHEN Response IS NULL OR Response = '' THEN 1 ELSE 0 END) AS Response_blank_count
FROM train;




SELECT	
	MIN("Age") AS min_age,
    MAX("Age") AS max_age,
    AVG("Age") AS avg_age,
    
    MIN("Annual_Premium") AS min_premium,
    MAX("Annual_Premium") AS max_premium,
    AVG("Annual_Premium") AS avg_premium,
    
    MIN("Vintage") AS min_vintage,
    MAX("Vintage") AS max_vintage,
    AVG("Vintage") AS avg_vintage,

    -- 3. BINARY FLAG VALIDATION (Ensuring values are strictly 0 or 1)
    SUM(CASE WHEN "Driving_License" NOT IN (0, 1) THEN 1 ELSE 0 END) AS invalid_dl_flags,
    SUM(CASE WHEN "Previously_Insured" NOT IN (0, 1) THEN 1 ELSE 0 END) AS invalid_prev_insured_flags,
    SUM(CASE WHEN "Response" NOT IN (0, 1) THEN 1 ELSE 0 END) AS invalid_response_flags,

    -- 4. CARDINALITY (How many distinct regions/channels exist)
    COUNT(DISTINCT "Region_Code") AS distinct_regions,
    COUNT(DISTINCT "Policy_Sales_Channel") AS distinct_channels
from train;


SELECT "Gender", COUNT(*) FROM "train" GROUP BY 1;
SELECT "Vehicle_Age", COUNT(*) FROM "train" GROUP BY 1;
SELECT "Vehicle_Damage", COUNT(*) FROM "train" GROUP BY 1;


SELECT 
    COUNT(*) AS exact_match_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM "train"), 2) AS percentage_of_dataset,
    (SELECT MIN("Annual_Premium") FROM "train") AS absolute_minimum_premium
FROM "train"
WHERE "Annual_Premium" = 2630;


SELECT 
    COUNT(*) AS outlier_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM "train"), 2) AS percentage_of_dataset,
    MIN("Annual_Premium") AS lowest_outlier,
    MAX("Annual_Premium") AS highest_outlier
FROM "train"
WHERE "Annual_Premium" > 100000;



WITH ChannelCounts AS (
    SELECT 
        "Policy_Sales_Channel",
        COUNT(*) AS row_count
    FROM "train"
    GROUP BY "Policy_Sales_Channel"
)
SELECT 
    "Policy_Sales_Channel",
    row_count,
    -- Individual percent calculated by dividing by the global window sum
    ROUND(100.0 * row_count / SUM(row_count) OVER (), 2) AS pct_of_total,
    -- Running total of raw counts divided by the global window sum at the very end
    ROUND(
        100.0 * SUM(row_count) OVER (
            ORDER BY row_count DESC, "Policy_Sales_Channel" ASC
            ROWS UNBOUNDED PRECEDING
        ) / SUM(row_count) OVER (), 
        2
    ) AS cumulative_pct
FROM ChannelCounts
ORDER BY row_count DESC, "Policy_Sales_Channel" ASC;



WITH RegionCounts AS (
    SELECT 
        "Region_Code",
        COUNT(*) AS row_count
    FROM "train"
    GROUP BY "Region_Code"
)
SELECT 
    "Region_Code",
    row_count,
    -- Individual percent using the global window sum as the denominator
    ROUND(100.0 * row_count / SUM(row_count) OVER (), 2) AS pct_of_total,
    -- Cumulative percent calculated using raw integers, a physical frame, and a tiebreaker
    ROUND(
        100.0 * SUM(row_count) OVER (
            ORDER BY row_count DESC, "Region_Code" ASC
            ROWS UNBOUNDED PRECEDING
        ) / SUM(row_count) OVER (), 
        2
    ) AS cumulative_pct
FROM RegionCounts
ORDER BY row_count DESC, "Region_Code" ASC;


SELECT 
    COUNT(*) AS total_records,
    SUM("Response") AS total_positive_responses,
    ROUND(100.0 * SUM("Response") / COUNT(*), 2) AS response_rate_percentage
FROM "train";