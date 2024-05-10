import time
import psycopg2
import argparse
import csv

DBname = "postgres"
DBuser = "postgres"
DBpwd = "Bhuvana@26"
TableName = 'CensusData'
Datafile = "filedoesnotexist"  # Name of the data file to be loaded
CreateDB = False  # Indicates whether the DB table should be (re)-created

def row2vals(row):
    for key in row:
        if not row[key]:
            row[key] = 0  # ENHANCE: handle the null vals
        row['County'] = row['County'].replace('\'','')  # TIDY: eliminate quotes within literals

    ret = f"""
       {row['CensusTract']},            -- CensusTract
       '{row['State']}',                -- State
       '{row['County']}',               -- County
       {row['TotalPop']},               -- TotalPop
       {row['Men']},                    -- Men
       {row['Women']},                  -- Women
       {row['Hispanic']},               -- Hispanic
       {row['White']},                  -- White
       {row['Black']},                  -- Black
       {row['Native']},                 -- Native
       {row['Asian']},                  -- Asian
       {row['Pacific']},                -- Pacific
       {row['Citizen']},                -- Citizen
       {row['Income']},                 -- Income
       {row['IncomeErr']},              -- IncomeErr
       {row['IncomePerCap']},           -- IncomePerCap
       {row['IncomePerCapErr']},        -- IncomePerCapErr
       {row['Poverty']},                -- Poverty
       {row['ChildPoverty']},           -- ChildPoverty
       {row['Professional']},           -- Professional
       {row['Service']},                -- Service
       {row['Office']},                 -- Office
       {row['Construction']},           -- Construction
       {row['Production']},             -- Production
       {row['Drive']},                  -- Drive
       {row['Carpool']},                -- Carpool
       {row['Transit']},                -- Transit
       {row['Walk']},                   -- Walk
       {row['OtherTransp']},            -- OtherTransp
       {row['WorkAtHome']},             -- WorkAtHome
       {row['MeanCommute']},            -- MeanCommute
       {row['Employed']},               -- Employed
       {row['PrivateWork']},            -- PrivateWork
       {row['PublicWork']},             -- PublicWork
       {row['SelfEmployed']},           -- SelfEmployed
       {row['FamilyWork']},             -- FamilyWork
       {row['Unemployment']}            -- Unemployment
    """

    return ret


def initialize():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datafile", required=True)
    args = parser.parse_args()

    global Datafile
    Datafile = args.datafile

# Read the input data file into a list of row strings
def readdata(fname):
    print(f"readdata: reading from File: {fname}")
    with open(fname, mode="r") as fil:
        dr = csv.DictReader(fil)
        
        rowlist = []
        for row in dr:
            rowlist.append(row)

    return rowlist

# Convert list of data rows into list of SQL 'INSERT INTO ...' commands
def getSQLcmnds(rowlist):
    cmdlist = []
    for row in rowlist:
        valstr = row2vals(row)
        cmd = f"INSERT INTO {TableName} VALUES ({valstr});"
        cmdlist.append(cmd)
    return cmdlist

# Connect to the database
def dbconnect():
    connection = psycopg2.connect(
        host="localhost",
        database=DBname,
        user=DBuser,
        password=DBpwd,
    )
    connection.autocommit = False
    return connection

# Load data into the database
def load(conn, icmdlist):
    with conn.cursor() as cursor:
        print(f"Loading {len(icmdlist)} rows")
        start = time.perf_counter()
        
        for cmd in icmdlist:
            cursor.execute(cmd)
        
        elapsed = time.perf_counter() - start
        print(f'Finished Loading. Elapsed Time: {elapsed:0.4} seconds')
        
        # Commit the changes to the database
        conn.commit()

    # Now, create the primary key and index after loading data
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE INDEX idx_{TableName}_State ON {TableName}(State);")
        print("Added Index")

# Main function
def main():
    initialize()
    conn = dbconnect()
    rlis = readdata(Datafile)
    cmdlist = getSQLcmnds(rlis)

    load(conn, cmdlist)

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()
