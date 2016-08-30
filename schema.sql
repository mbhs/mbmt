drop table if exists team;
create table team (
	id integer primary key autoincrement,
	name text not null,
	score integer,
	foreign key(school) references school(id)
);

drop table if exists school;
create table school (
  id integer primary key autoincrement,
	name text not null
);