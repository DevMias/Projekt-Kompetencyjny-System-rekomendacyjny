
drop database if exists recommendation_system;
create database recommendation_system;

use recommendation_system;

-- usuwanie tabel

drop table if exists Friends;
drop table if exists Order_Details;
drop table if exists Orders;
drop table if exists Users;
drop table if exists Products_Key_Words;
drop table if exists Key_Words;
drop table if exists Products;
drop table if exists Categories;

-- tworzenie tabel

create table Users (
    id int not null IDENTITY(1,1),
    external_ref varchar(100) unique not null,
    name varchar(100) not null,
    second_name varchar(100) not null,
    birthday date not null,
    email varchar(254) not null,
    password varchar(100) not null,
    constraint PK_Users primary key (id)
)


create table Friends (
    user_ref int not null,
    friend_ref int not null,
    foreign key (user_ref) references Users(id),
    foreign key (friend_ref) references Users(id)
)

CREATE UNIQUE INDEX unique_friends_user_ref_friend_ref ON Friends (user_ref, friend_ref)

create Table Orders (
    id int not null IDENTITY(1,1),
    user_ref int not null,
    bought_at date not null,
    constraint PK_Orders primary key (id),
    foreign key (user_ref) references Users(id)
)

create table Categories (
    id int not null IDENTITY(1,1),
    name varchar(100) not null,
    constraint PK_Categories primary key (id)
)

create table Products (
    id int not null IDENTITY(1,1),
    external_ref varchar(100) unique not null,
    name varchar(100) not null,
    category_ref int not null,
    price float not null,
    constraint PK_Products primary key (id),
    foreign key (category_ref) references Categories(id)
)

create table Order_Details (
    order_ref int not null,
    product_ref int not null,
    quantity int not null,
    foreign key (order_ref) references Orders(id),
    foreign key (product_ref) references Products(id)
)

create table Key_Words (
    id int not null IDENTITY(1,1),
    name varchar(100) not null,
    constraint PK_Key_Words primary key (id)
)

create table Products_Key_Words (
    product_ref int not null,
    key_word_ref int not null,
    foreign key (product_ref) references Products(id),
    foreign key (key_word_ref) references Key_Words(id)
)



