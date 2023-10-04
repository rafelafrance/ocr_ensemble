CANNED_INSERTS = {
    "cache": """
        insert into cache ( hash,  path,  labels,  ocr)
        values            (:hash, :path, :labels, :ocr);
        """,
    "char_sub_matrix": """
        insert into char_sub_matrix
               ( char1,  char2,  char_set,  score,  sub)
        values (:char1, :char2, :char_set, :score, :sub);
        """,
    "label_tests": """
        insert into label_tests
               ( test_set,   train_set,  sheet_id,    test_class,  test_conf,
                 test_left,  test_top,   test_right,  test_bottom)
        values (:test_set,  :train_set, :sheet_id,   :test_class, :test_conf,
                :test_left, :test_top,  :test_right, :test_bottom);
        """,
    "label_train": """
        insert into label_train
               ( train_set,   sheet_id,  train_class,
                 train_left,  train_top,  train_right,  train_bottom)
        values (:train_set,  :sheet_id, :train_class,
                :train_left, :train_top, :train_right, :train_bottom);
        """,
    "labels": """
        insert into labels
               ( sheet_id,    label_set,  class,        label_conf,
                 label_left,  label_top,  label_right,  label_bottom)
        values (:sheet_id,   :label_set, :class,       :label_conf,
                :label_left, :label_top, :label_right, :label_bottom);
        """,
    "ocr_scores": """
        insert into ocr_scores
               ( score_set,   label_id,  gold_id,  gold_set,  pipeline,
                 score_text,  score)
        values (:score_set,  :label_id, :gold_id, :gold_set, :pipeline,
                :score_text, :score)
        """,
    "ocr_texts": """
        insert into ocr_texts
               ( label_id,  ocr_set,  ocr_text)
        values (:label_id, :ocr_set, :ocr_text);
        """,
    "sheets": """
        insert into sheets
               ( sheet_set,  path,  width,  height,  core_id,  split)
        values (:sheet_set, :path, :width, :height, :core_id, :split);
        """,
    "traits": """
        insert into traits ( trait_set,  ocr_id,  trait,  data)
                    values (:trait_set, :ocr_id, :trait, :data);
        """,
}

CANNED_SELECTS = {
    "cache": """
        select * from cache where path = :path and hash = :hash
        """,
    "char_sub_matrix": """
        select * from char_sub_matrix where char_set = :char_set
        """,
    "gold_standard": """
        select *
        from   gold_standard
        join   labels using (label_id)
        join   sheets using (sheet_id)
        where  gold_set = :gold_set
        """,
    "label_test": """
        select *
        from   label_tests
        join   sheets using (sheet_id)
        where  test_set  =  :test_set
        and    train_set =  :train_set
        and    test_conf >= :test_conf
        order by sheet_id
        """,
    "label_train": """
        select *
        from   label_train
        join   sheets using (sheet_id)
        where  split = :split
        and    train_set = :train_set
        order by sheet_id
        """,
    "label_train_split": """
        select    *
        from      sheets
        left join label_train using (sheet_id)
        where     split = :split
        and       train_set = :train_set
        """,
    "labels": """
        select *
        from   labels
        join   sheets using (sheet_id)
        where  label_set = :label_set
        and    label_conf >= :label_conf
        """,
    "ocr_scores": """
        select * from ocr_scores where score_set = :score_set
        """,
    "ocr_texts": """
        select *
        from   ocr_texts
        join   labels using (label_id)
        join   sheets using (sheet_id)
        where  ocr_set = :ocr_set
        """,
    "sheets": """
        select * from sheets where sheet_set = :sheet_set
        """,
    "sheets_shuffle": """
        select sheet_id from sheets
        where  sheet_set = :sheet_set
        order by random()
        """,
    "sheets_split": """
        select * from sheets where sheet_set = :sheet_set and split = :split
        """,
    "traits": """
        select *
        from   traits
        join   ocr_texts using (ocr_id)
        join   labels using (label_id)
        join   sheets using (sheet_id)
        where  trait_set = :trait_set
        order by ocr_id, trait_id
        """,
}


CANNED_DELETES = {
    "char_sub_matrix": """
        delete from char_sub_matrix where char_set = :char_set
        """,
    "labels": """
        delete from labels where label_set = :label_set
        """,
    "label_tests": """
        delete from label_tests where test_set = :test_set and train_set = :train_set
        """,
    "label_train": """
        delete from label_train where train_set = :train_set
        """,
    "ocr_scores": """
        delete from ocr_scores where score_set = :score_set
        """,
    "ocr_texts": """
        delete from ocr_texts where ocr_set = :ocr_set
        """,
    "sheets": """
        delete from sheets where sheet_set = :sheet_set
        """,
    "traits": """
        delete from traits where trait_set = :trait_set
        """,
}
