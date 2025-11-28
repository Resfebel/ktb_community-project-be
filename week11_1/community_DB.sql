create database ktb_community_db;
use ktb_community_db;

# create table
create table user (
	user_id int primary key auto_increment,
    email VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(10) NOT NULL,
    profile_image VARCHAR(255) default NULL
);

create table post (
	post_id int primary key auto_increment,
    user_id int NOT NULL,
    title VARCHAR(26) NOT NULL,
    content TEXT NOT NULL,
    post_image VARCHAR(255) default NULL,
    create_at TIMESTAMP default CURRENT_TIMESTAMP,
    likes int default 0,
    views int default 0,
    comments int default 0,
    foreign key (user_id) references user(user_id) ON DELETE CASCADE
);

create table comment (
	comment_id int primary key auto_increment,
    post_id int NOT NULL,
    commenter_id int NOT NULL,
    comment_text TEXT NOT NULL,
    create_at TIMESTAMP default CURRENT_TIMESTAMP,
    foreign key (post_id) references post(post_id) ON DELETE CASCADE,
    foreign key (commenter_id) references user(user_id) ON DELETE CASCADE
);

create table postlike (
	post_id int NOT NULL,
    user_id int NOT NULL,
    primary key (post_id, user_id),
    foreign key (post_id) references post(post_id) ON DELETE CASCADE,
    foreign key (user_id) references user(user_id) ON DELETE CASCADE
);
