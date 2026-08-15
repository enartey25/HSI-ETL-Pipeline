create table if not exists hsi_features (
    trade_date       DATE PRIMARY KEY,
    open             NUMERIC(12,4) NOT NULL,
    high             NUMERIC(12,4) NOT NULL,
    low              NUMERIC(12,4) NOT NULL,
    close            NUMERIC(12,4) NOT NULL,
    volume           BIGINT NOT NULL,
    daily_return     NUMERIC(10,6),
    daily_range      NUMERIC(12,4),
    adr_14d          NUMERIC(12,4),
    gap_pct          NUMERIC(10,6),
    clv              NUMERIC(10,6),
    vol_change       NUMERIC(10,6),
    vol_ag_20dayavg  NUMERIC(10,6),
    created_at       TIMESTAMP DEFAULT now(),
    updated_at       TIMESTAMP DEFAULT now()
);