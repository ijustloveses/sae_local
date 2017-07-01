create table users (id varchar(200) not null, name varchar(200) not null, auth_token varchar(200) not null, expired_time real not null, primary key(id)) DEFAULT CHARSET=utf8;

create table posts(
	id int not null auto_increment,
    uid varchar(200) not null,
	created_at datetime not null,
	post_text TEXT not null,
	primary key(id),
	index(created_at)
) DEFAULT CHARSET=utf8;

create table tags(id int not null auto_increment, name varchar(200) not null, primary key(id)) DEFAULT CHARSET=utf8;
create unique index idx_tags_name on tags (name);

create table posts_tags(pid int not null, tid int not null, uid varchar(200) not null, index(pid), index(tid), index(uid)) DEFAULT CHARSET=utf8;
