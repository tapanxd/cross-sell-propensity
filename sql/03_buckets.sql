SELECT
    -- Count of records in train_cleaned that do not exist in channel_map
    SUM(CASE WHEN c.channel_code IS NULL THEN 1 ELSE 0 END) AS orphan_channel_count,
    
    -- Count of records in train_cleaned that do not exist in region_map
    SUM(CASE WHEN r.region_code IS NULL THEN 1 ELSE 0 END) AS orphan_region_count
FROM "train_cleaned" m
LEFT JOIN "channel_map" c 
    ON m."Policy_Sales_Channel" = c.channel_code
LEFT JOIN "region_map" r 
    ON m."Region_Code" = r.region_code;\
	
	
	
	
WITH NonBaseBuckets AS (
    -- Step 1: Assign rows to buckets using NTILE over the ordered continuous distribution
    SELECT 
        "Annual_Premium",
        NTILE(3) OVER (ORDER BY "Annual_Premium" ASC) AS tercile_bucket,
        NTILE(2) OVER (ORDER BY "Annual_Premium" ASC) AS median_bucket
    FROM "train_cleaned"
    --WHERE "Annual_Premium" > 2630
)
-- Step 2: Aggregate the buckets to extract the boundary cut points
SELECT
    -- Total count of rows outside the spike
    COUNT(*) AS non_base_count,
    
    -- The maximum values of Tercile 1 and Tercile 2 are your two continuous cut points
    MAX(CASE WHEN tercile_bucket = 1 THEN "Annual_Premium" END) AS continuous_33rd_percentile,
    MAX(CASE WHEN tercile_bucket = 2 THEN "Annual_Premium" END) AS continuous_66th_percentile,
    
    -- The maximum value of Median Bucket 1 is your continuous median cut point
    MAX(CASE WHEN median_bucket = 1 THEN "Annual_Premium" END) AS continuous_median
FROM NonBaseBuckets;