-- Add AWIPS PIL to text_products
ALTER TABLE text_products DROP reads;
ALTER TABLE text_products ADD pil char(6);
ALTER TABLE text_products ADD product_num smallint;
CREATE INDEX text_products_pil_index on text_products(pil);
