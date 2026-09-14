-- Database schema, MySQL dialect so it opens in MySQL Workbench
-- (File > Open SQL Script, or Import > Reverse Engineer MySQL Create Script for the diagram).
--
-- The app runs on PostgreSQL and the migrations are the source of truth; the columns, keys and
-- indexes below match them one to one. Only the type spellings differ, as MySQL has no equivalents:
--   TIMESTAMPTZ -> DATETIME(6)    BOOLEAN -> TINYINT(1)    INET -> VARCHAR(45)
--   BIGSERIAL   -> BIGINT AUTO_INCREMENT

-- staff accounts for the Django admin only; visitors never appear here
CREATE TABLE users_user (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    password     VARCHAR(128) NOT NULL,
    last_login   DATETIME(6) NULL,
    is_superuser TINYINT(1) NOT NULL DEFAULT 0,
    username     VARCHAR(150) NOT NULL UNIQUE,
    first_name   VARCHAR(150) NOT NULL DEFAULT '',
    last_name    VARCHAR(150) NOT NULL DEFAULT '',
    email        VARCHAR(254) NOT NULL DEFAULT '',
    is_staff     TINYINT(1) NOT NULL DEFAULT 0,
    is_active    TINYINT(1) NOT NULL DEFAULT 1,
    date_joined  DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Identity lives on the comment: the form fills it in and there are no accounts.
CREATE TABLE comments_comment (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    author_name     VARCHAR(64) NOT NULL,
    author_email    VARCHAR(254) NOT NULL,
    author_homepage VARCHAR(200) NOT NULL DEFAULT '',
    parent_id       BIGINT NULL,
    text            TEXT NOT NULL,
    text_raw        TEXT NOT NULL,
    created_at      DATETIME(6) NOT NULL,
    ip              VARCHAR(45) NULL,
    user_agent      VARCHAR(255) NOT NULL DEFAULT '',
    is_deleted      TINYINT(1) NOT NULL DEFAULT 0,
    lft             INT UNSIGNED NOT NULL,
    rght            INT UNSIGNED NOT NULL,
    tree_id         INT UNSIGNED NOT NULL,
    level           INT UNSIGNED NOT NULL,
    CONSTRAINT fk_comment_parent FOREIGN KEY (parent_id) REFERENCES comments_comment (id) ON DELETE CASCADE,
    INDEX ix_comment_created (created_at),
    INDEX ix_comment_author_name (author_name),
    INDEX ix_comment_author_email (author_email),
    INDEX ix_comment_parent (parent_id),
    INDEX ix_comment_tree (tree_id, lft),
    INDEX ix_comment_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE comments_attachment (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    comment_id    BIGINT NOT NULL,
    kind          VARCHAR(8) NOT NULL,
    file          VARCHAR(100) NOT NULL,
    original_name VARCHAR(255) NOT NULL DEFAULT '',
    size          INT UNSIGNED NOT NULL DEFAULT 0,
    created_at    DATETIME(6) NOT NULL,
    CONSTRAINT fk_attachment_comment FOREIGN KEY (comment_id) REFERENCES comments_comment (id) ON DELETE CASCADE,
    INDEX ix_attachment_comment (comment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE captcha_captchastore (
    id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    challenge  VARCHAR(32) NOT NULL,
    response   VARCHAR(32) NOT NULL,
    hashkey    VARCHAR(40) NOT NULL UNIQUE,
    expiration DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
