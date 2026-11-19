# Veri modeli (ilk taslak)

```sql
CREATE TABLE source (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('news','official','community')),
  reliability REAL NOT NULL DEFAULT 0.5   -- 0..1
);

CREATE TABLE event (
  id BIGSERIAL PRIMARY KEY,
  kind TEXT NOT NULL,                      -- fight, stabbing, assault ...
  occurred_at TIMESTAMPTZ NOT NULL,
  geom GEOGRAPHY(Point, 4326) NOT NULL,
  source_id INT REFERENCES source(id),
  source_url TEXT,
  confidence REAL NOT NULL DEFAULT 0.5     -- 0..1
);

CREATE TABLE area (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  boundary GEOGRAPHY(MultiPolygon, 4326) NOT NULL
);

-- Sonraki aşama: anonim, süreli kayıtlar
CREATE TABLE report (
  id BIGSERIAL PRIMARY KEY,
  geom GEOGRAPHY(Point, 4326) NOT NULL,
  kind TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at TIMESTAMPTZ NOT NULL          -- kısa sürede otomatik silinir
);
```
