sql_table_offers = """ CREATE TABLE IF NOT EXISTS offers (
                    id integer PRIMARY KEY,
                    offer_id text NOT NULL UNIQUE,
                    job_name text NOT NULL,
                    category text,
                    company text NOT NULL,
                    tech_main text,
                    get_ts text,
                    sent_cv text NOT NULL,
                    sent_ts text,
                    contact text,
                    link text NOT NULL
                    ); """
sql_table_cities = """ CREATE TABLE IF NOT EXISTS cities (
                    name text PRIMARY KEY
                    ); """
sql_table_offers_cities = """ CREATE TABLE IF NOT EXISTS offers_cities (
                    offer_id integer,
                    city_name integer,
                    FOREIGN KEY (offer_id) REFERENCES offers (offer_id),
                    FOREIGN KEY (city_name) REFERENCES cities (name),
                    UNIQUE(offer_id, city_name)
                    ); """
sql_table_technology = """ CREATE TABLE IF NOT EXISTS technology (
                    name text PRIMARY KEY
                    ); """
sql_table_offers_tech = """ CREATE TABLE IF NOT EXISTS offers_tech (
                    offer_id integer,
                    tech_name integer,
                    FOREIGN KEY (offer_id) REFERENCES offers (offer_id),
                    FOREIGN KEY (tech_name) REFERENCES technology (name),
                    UNIQUE(offer_id, tech_name)
                    ); """
