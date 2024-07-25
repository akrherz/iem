<?php

/** @generate-function-entries */

/**
 * @return resource|false
 */
function dbase_open(string $path, int $mode) {}

/**
 * @param resource $database
 */
function dbase_close($database): bool {}

/**
 * @param resource $database
 */
function dbase_add_record($database, array $data): bool {}

/**
 * @param resource $database
 */
function dbase_delete_record($database, int $number): bool {}

/**
 * @param resource $database
 */
function dbase_replace_record($database, array $data, int $number): bool {}

/**
 * @param resource $database
 */
function dbase_numrecords($database): int {}

/**
 * @param resource $database
 */
function dbase_numfields($database): int {}

/**
 * @param resource $database
 */
function dbase_pack($database): bool {}

/**
 * @param resource $database
 */
function dbase_get_record($database, int $number): array|false {}

/**
 * @param resource $database
 */
function dbase_get_record_with_names($database, int $number): array|false {}

/**
 * @return resource|false
 */
function dbase_create(string $path, array $fields, int $type = DBASE_TYPE_DBASE) {}

/**
 * @param resource $database
 */
function dbase_get_header_info($database): array {}

