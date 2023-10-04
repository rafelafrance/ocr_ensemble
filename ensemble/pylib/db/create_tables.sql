create table if not exists gold_standard (
    gold_id     integer primary key autoincrement,
    sheet_id    integer,
    label_id    integer,
    gold_set    text,
    gold_text   text,
    transcriber text,
    validator   text,
    notes       text
);


create table if not exists label_tests (
    test_id     integer primary key autoincrement,
    test_set    text,
    train_set   text,
    sheet_id    integer,
    test_class  text,
    test_conf   real,
    test_left   integer,
    test_top    integer,
    test_right  integer,
    test_bottom integer
);


create table if not exists label_train (
    train_id     integer primary key autoincrement,
    train_set    text,
    sheet_id     integer,
    train_class  text,
    train_left   integer,
    train_top    integer,
    train_right  integer,
    train_bottom integer
);


create table if not exists labels (
    label_id     integer primary key autoincrement,
    sheet_id     integer,
    label_set    text,
    class        text,
    label_conf   real,
    label_left   integer,
    label_top    integer,
    label_right  integer,
    label_bottom integer
);
create index if not exists labels_sheet_id on labels (sheet_id);


create table if not exists ocr_scores (
    score_id   integer primary key autoincrement,
    label_id   integer,
    gold_id    integer,
    gold_set   text,
    score_set  text,
    pipeline   text,
    score_text text,
    score      integer
);


create table if not exists ocr_texts (
    ocr_id     integer primary key autoincrement,
    label_id   integer,
    ocr_set    text,
    ocr_text   text
);
create index if not exists ocr_label_id on ocr_texts (label_id);


create table if not exists sheets (
    sheet_id  integer primary key autoincrement,
    sheet_set text,
    path      text,
    width     integer,
    height    integer,
    core_id   text,
    split     text
);


create table if not exists sheet_errors (
    error_id integer primary key autoincrement,
    path     text    unique
);


create table if not exists subjects_to_sheets (
    subject_id integer primary key,
    path       text,
    core_id    text
);
create index if not exists subs_to_sheets_idx on subjects_to_sheets (core_id);


create table if not exists traits (
    trait_id  integer primary key autoincrement,
    trait_set text,
    ocr_id    integer,
    trait     text,
    data      text
);
create index if not exists traits_trait_set on traits (trait_set);
create index if not exists traits_ocr_id on traits (ocr_id);
create index if not exists traits_trait on traits (trait);


create table if not exists cache (
    hash   text,
    path   text,
    labels text,
    ocr    text
);
create index if not exists cache_hash on cache (hash, path);
