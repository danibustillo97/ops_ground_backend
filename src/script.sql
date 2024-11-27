    SELECT * FROM bender.Tbl_Baggage_Case_Ground_Ops
    ORDER BY last_updated DESC 

TRUNCATE TABLE bender.Tbl_Baggage_Case_Ground_Ops

SELECT Confirmation_Num, Bag_Tags  FROM Minerva.Fct_Manifest





WITH FlightData AS (
    SELECT
        fifsf.[datetime],
        fifsf.datetime_Local,
        fifsf.date AS flight_date,
        fifsf.DEP AS Departure_Airport,
        fifsf.ARR AS Arrival_Airport,
        fifsf.FLT,
        fifsf.reg,
        fifsf.inFuel,
        fifsf.outFuel,
        ROW_NUMBER() OVER (PARTITION BY fifsf.reg ORDER BY fifsf.datetime_Local) AS rn,
        LAG(fifsf.inFuel) OVER (PARTITION BY fifsf.reg ORDER BY fifsf.datetime_Local) AS Previous_InFuel,
        LAG(fifsf.outFuel) OVER (PARTITION BY fifsf.reg ORDER BY fifsf.datetime_Local) AS Previous_OutFuel,
        LAG(fifsf.FLT) OVER (PARTITION BY fifsf.reg ORDER BY fifsf.datetime_Local) AS Previous_Flight
    FROM Minerva.Minerva.Fct_IOCC_Flight_Schedule_Fuel fifsf
),
FuelData AS (
    SELECT
        fd.flight_date,
        fd.datetime_Local,
        fd.Departure_Airport,
        fd.Arrival_Airport,
        fd.FLT,
        fd.reg,
        fd.inFuel,
        fd.outFuel,
        fd.Previous_InFuel,
        fd.Previous_OutFuel,
        fd.outFuel - COALESCE(fd.Previous_InFuel, 0) AS FuelUpLift,
        LAG(fd.outFuel - COALESCE(fd.Previous_InFuel, 0)) OVER (PARTITION BY fd.reg ORDER BY fd.datetime_Local) AS Previous_FuelUpLift
    FROM FlightData fd
),
PriceData AS (
    SELECT
        fd.flight_date,
        fd.datetime_Local,
        fd.Departure_Airport,
        fd.Arrival_Airport,
        fd.FLT,
        fd.reg,
        fd.inFuel,
        fd.outFuel,
        fd.Previous_InFuel,
        fd.FuelUpLift,
        fd.Previous_FuelUpLift,
        COALESCE(fp.Fuel_Price, fp2.Fuel_Price) AS Fuel_Price,
        CASE
            WHEN fd.Previous_FuelUpLift <= 0 THEN 
                ((fd.inFuel * LAG(COALESCE(fp.Fuel_Price, fp2.Fuel_Price)) OVER (PARTITION BY fd.reg ORDER BY fd.datetime_Local)) + 
                (fd.FuelUpLift * COALESCE(fp.Fuel_Price, fp2.Fuel_Price))) / NULLIF(fd.inFuel + fd.FuelUpLift, 0)
            WHEN fd.FuelUpLift <= 0 THEN 
                LAG(COALESCE(fp.Fuel_Price, fp2.Fuel_Price)) OVER (PARTITION BY fd.reg ORDER BY fd.datetime_Local)
            WHEN fd.Previous_FuelUpLift > 0 AND fd.FuelUpLift > 0 THEN 
                ((fd.Previous_FuelUpLift * LAG(COALESCE(fp.Fuel_Price, fp2.Fuel_Price)) OVER (PARTITION BY fd.reg ORDER BY fd.datetime_Local)) + 
                (fd.FuelUpLift * COALESCE(fp.Fuel_Price, fp2.Fuel_Price))) / NULLIF(fd.Previous_FuelUpLift + fd.FuelUpLift, 0)
            ELSE COALESCE(fp.Fuel_Price, fp2.Fuel_Price)
        END AS AvgPricePerFuelConsumption
    FROM FuelData fd
    LEFT JOIN bender.tbl_fuel_price_vendor_report fp
        ON fd.Departure_Airport = fp.Airport AND fd.flight_date BETWEEN fp.StartDate AND fp.EndDate
    LEFT JOIN bender.tbl_fuel_price_vendor_report fp2
        ON fd.Arrival_Airport = fp2.Airport AND fd.flight_date BETWEEN fp2.StartDate AND fp2.EndDate
),
AggregatedData AS (
    SELECT
        Departure_Airport,
        Arrival_Airport,
        datetime_Local,
        flight_date,
        reg,
        SUM(FuelUpLift) AS Total_Uplift,
        SUM(FuelUpLift * AvgPricePerFuelConsumption) / NULLIF(SUM(FuelUpLift), 0) AS Total_AvgPricePerFuelConsumption,
        AVG(COALESCE(fp.Fuel_Price, fp2.Fuel_Price)) AS AVG_Price
    FROM PriceData fd
    LEFT JOIN bender.tbl_fuel_price_vendor_report fp
        ON fd.Departure_Airport = fp.Airport AND fd.flight_date BETWEEN fp.StartDate AND fp.EndDate
    LEFT JOIN bender.tbl_fuel_price_vendor_report fp2
        ON fd.Arrival_Airport = fp2.Airport AND fd.flight_date BETWEEN fp2.StartDate AND fp2.EndDate
    GROUP BY Departure_Airport, Arrival_Airport, datetime_Local, flight_date, reg
),
TotalAvgPrice AS (
    SELECT
        Departure_Airport,
        Arrival_Airport,
        datetime_Local,
        flight_date,
        reg,
        AVG(AVG_Price) AS Total_Avg_Price,
        SUM(Total_Uplift) AS Total_Uplift,
        SUM(Total_Uplift * Total_AvgPricePerFuelConsumption) / NULLIF(SUM(Total_Uplift), 0) AS Final_AvgPricePerFuelConsumption
    FROM AggregatedData
    GROUP BY Departure_Airport, Arrival_Airport, datetime_Local, flight_date, reg
) 
SELECT
    Departure_Airport,
    Arrival_Airport,
    datetime_Local,
    flight_date,
    reg,
    Total_Avg_Price,
    Total_Uplift,
    Final_AvgPricePerFuelConsumption
FROM TotalAvgPrice
ORDER BY datetime_Local ; 

