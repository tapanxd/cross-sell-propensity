-- 02_clean.sql
DROP TABLE IF EXISTS "train_cleaned";

-- Recreate table with constraints and correct codes stored as float by the source system
CREATE TABLE "train_cleaned" (
    "id"                   INTEGER PRIMARY KEY, -- Enforces uniqueness loudly and flags duplicate imports to prevent silent data corruption
    "Gender"               TEXT NOT NULL,
    "Age"                  INTEGER NOT NULL,
    "Driving_License"      INTEGER NOT NULL,
    "Region_Code"          INTEGER NOT NULL,    -- Corrected from REAL because they are codes
    "Previously_Insured"   INTEGER NOT NULL,
    "Vehicle_Age"          TEXT NOT NULL,
    "Vehicle_Damage"       TEXT NOT NULL,
    "Annual_Premium"       REAL NOT NULL,
    "Policy_Sales_Channel" INTEGER NOT NULL,    -- Corrected from REAL because they are codes
    "Vintage"              INTEGER NOT NULL,
    "Response"             INTEGER NOT NULL
);

-- Profiling verified all codes end in .0; these casts are safe to run without data loss
INSERT INTO "train_cleaned" (
    "id", "Gender", "Age", "Driving_License", "Region_Code", 
    "Previously_Insured", "Vehicle_Age", "Vehicle_Damage", 
    "Annual_Premium", "Policy_Sales_Channel", "Vintage", "Response"
)
SELECT 
    "id", 
    "Gender", 
    "Age", 
    "Driving_License",
    CAST("Region_Code" AS INTEGER), 
    "Previously_Insured", 
    "Vehicle_Age", 
    "Vehicle_Damage", 
    "Annual_Premium",
    CAST("Policy_Sales_Channel" AS INTEGER), 
    "Vintage", 
    "Response"
FROM "train";

-- Verification checkpoint to ensure no records vanished during transfer
SELECT 
    (SELECT COUNT(*) FROM "train") AS source_row_count,
    (SELECT COUNT(*) FROM "train_cleaned") AS target_row_count,
    (SELECT COUNT(*) FROM "train") - (SELECT COUNT(*) FROM "train_cleaned") AS rows_delta;