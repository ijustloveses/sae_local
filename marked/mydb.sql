
create table users (id varchar(200) not null, name varchar(200) not null, auth_token varchar(200) not null, expired_time real not null, primary key(id)) DEFAULT CHARSET=utf8;

create table raw_posts(content text not null) DEFAULT CHARSET=utf8;

create table uniq_raw_posts(id varchar(200) not null, content text not null, primary key(id)) DEFAULT CHARSET=utf8;

create table posts(
	id varchar(200) not null, 
	favtime datetime not null,
	created_at datetime not null,
	post_text TEXT not null,
	pic_urls TEXT not null,
	user_id varchar(200) not null, 
	profile_url varchar(200) not null,
	profile_image_url varchar(200) not null,
	screen_name varchar(200) not null,
	url varchar(200) not null, 
	re_id varchar(200) not null, 
	re_created_at datetime not null,
	re_post_text TEXT not null,
	re_pic_urls TEXT not null,
	re_user_id varchar(200) not null, 
	re_profile_url varchar(200) not null,
	re_profile_image_url varchar(200) not null,
	re_screen_name varchar(200) not null,
	re_url varchar(200) not null, 
	primary key(id),
	index(favtime)
) DEFAULT CHARSET=utf8;

create table tags(id varchar(200) not null, name varchar(200) not null, primary key(id)) DEFAULT CHARSET=utf8;

create table posts_tags(pid varchar(200) not null, tid varchar(200) not null, index(pid), index(tid)) DEFAULT CHARSET=utf8;

