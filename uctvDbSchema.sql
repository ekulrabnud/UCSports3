
drop table if exists chicagoLineupOTA;
drop table montrealLineup;

drop table if exists uctvLineups;
create table uctvLineups (
  id integer primary key autoincrement,
  lineupID text,
  channelNumber text not null,
  callsign text,
  name text,
  stationID integer,
  logoFileName text,
  uctvNo real
);