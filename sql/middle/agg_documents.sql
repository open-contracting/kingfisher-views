CREATE TABLE tmp_release_documents_aggregates AS
WITH all_document_types AS (
    SELECT
        id,
        documentType
    FROM
        award_documents_summary
    UNION ALL
    SELECT
        id,
        documentType
    FROM
        contract_documents_summary
    UNION ALL
    SELECT
        id,
        documentType
    FROM
        contract_implementation_documents_summary
    UNION ALL
    SELECT
        id,
        documentType
    FROM
        planning_documents_summary
    UNION ALL
    SELECT
        id,
        documentType
    FROM
        tender_documents_summary
)
SELECT
    id,
    jsonb_object_agg( coalesce(documentType, ''), documentType_count) total_documentType_counts,
    sum( documentType_count) total_documents
FROM (
    SELECT
        id,
        documentType,
        count(*) documentType_count
    FROM
        all_document_types
    GROUP BY
        id,
        documentType
) AS d
GROUP BY
    id;

CREATE UNIQUE INDEX tmp_release_documents_aggregates_id ON tmp_release_documents_aggregates (id);

