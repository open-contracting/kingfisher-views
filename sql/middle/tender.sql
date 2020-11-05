CREATE TABLE tmp_tender_summary AS
SELECT
    r.id,
    r.release_type,
    r.collection_id,
    r.ocid,
    r.release_id,
    r.data_id,
    data -> 'tender' AS tender
FROM
    tmp_release_summary_with_release_data r
WHERE
    data ? 'tender';

CREATE UNIQUE INDEX tmp_tender_summary_id ON tmp_tender_summary (id);

