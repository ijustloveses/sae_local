
create table users (id varchar(200) not null, name varchar(200) not null, auth_token varchar(200) not null, expired_time real not null, primary key(id)) DEFAULT CHARSET=utf8;

create table tvshow(
    id int not null auto_increment,
	uid varchar(70) not null,
	name varchar(30) not null, 
	season int not null,
	episode int not null,
	isdone boolean not null default false,
	primary key (`id`),
	unique(uid, name, season)
) DEFAULT CHARSET=utf8;

create table passwd(
    id int not null auto_increment,
	uid varchar(70) not null,
	project varchar(200) not null, 
	idno varchar(30) not null,
	passwd varchar(30) not null,
	primary key (`id`)
) DEFAULT CHARSET=utf8;

create table medicine(
    id int not null auto_increment,
	uid varchar(70) not null,
	statdate date not null, 
	stattype boolean not null default true,  -- false 禁止吃药 / true 必须吃药
	medicine tinyint not null,  -- 0 没吃 / 1 伊可新 / 2 Ddrop
	primary key (`id`),
	unique (statdate)
) DEFAULT CHARSET=utf8;

create table action(
    id int not null auto_increment,
	uid varchar(70) not null,
	statdate date not null,
	stattime time not null,
	action tinyint not null,  -- 1 sleep / 2 wakeup / 3 eat / 4 finish eating / 5 play / 6 pupu
	primary key (`id`)
) DEFAULT CHARSET=utf8;

create table sleeps(
    id int not null auto_increment,
	uid varchar(70) not null,
	statdate date not null,
	longmins int not null,
	shortmins int not null,
	primary key (`id`)
) DEFAULT CHARSET=utf8;