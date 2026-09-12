CREATE TABLE library (
    id INTEGER,
    book_id TEXT,
    book_name TEXT,
    book_pd TEXT,
    book_type TEXT,
    book_stock TEXT
);

INSERT INTO library (id, book_id, book_name, book_pd, book_type, book_stock) VALUES
    ('1', '00501.1', 'python 的二十個核心指南', '471212357', '資訊工程', '電腦工程'),
    ('2', '00501.2', 'C++的基本學尋手冊', '4710951253', '資訊工程', '資訊工程'),
    ('3', '00501.3', 'C 語言的核心學習法', '47100451257', '資訊工程', '資訊工程');