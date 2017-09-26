-- Add AWIPS PIL to text_products
ALTER TABLE text_products DROP reads;
ALTER TABLE text_products ADD pil char(6);
CREATE INDEX text_products_pil_index on text_products(pil);
