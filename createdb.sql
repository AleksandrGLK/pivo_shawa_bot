create table category(
    codename varchar(255) primary key,
    name varchar(255),
    aliases text
);

create table expense(
    id integer primary key,
    person_id integer,
    amount integer,
    created datetime,
    category_codename integer,
    raw_text text,
    FOREIGN KEY(category_codename) REFERENCES category(codename)
);

insert into category (codename, name, aliases)
values
    ("beer", "пиво", "корона, кб"),
    ("shaverma", "шаверма", "кебаб , шава, донер, шер");

