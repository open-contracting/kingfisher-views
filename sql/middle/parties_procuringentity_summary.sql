CREATE TABLE procuringEntity_summary AS
WITH r AS (
    SELECT
        *,
        data -> 'tender' -> 'procuringEntity' AS procuringEntity
    FROM
        tmp_release_summary_with_release_data
)
SELECT DISTINCT ON ( r.id)
    r.id,
    r.release_type,
    r.collection_id,
    r.ocid,
    r.release_id,
    r.data_id,
    procuringEntity,
    procuringEntity ->> 'id' AS procuringEntity_parties_id,
    ps.identifier AS procuringEntity_identifier,
    coalesce(procuringEntity ->> 'id', hyphenate(procuringEntity -> 'identifier' ->> 'scheme', procuringEntity -> 'identifier' ->> 'id'), procuringEntity ->> 'name'
) AS unique_identifier_attempt,
    ps.parties_additionalIdentifiers_ids AS procuringEntity_additionalIdentifiers_ids,
    ps.parties_additionalIdentifiers_count AS procuringEntity_additionalIdentifiers_count,
    CAST(ps.id IS NOT NULL AS integer
) AS link_to_parties,
    CAST(ps.id IS NOT NULL AND (ps.party -> 'roles') ? 'procuringEntity' AS integer
) AS link_with_role,
    ps.party_index
FROM
    r
    LEFT JOIN parties_summary ps ON r.id = ps.id
        AND (procuringEntity ->> 'id') = ps.parties_id
WHERE
    procuringEntity IS NOT NULL;

CREATE UNIQUE INDEX procuringEntity_summary_id ON procuringEntity_summary (id);

CREATE INDEX procuringEntity_summary_data_id ON procuringEntity_summary (data_id);

CREATE INDEX procuringEntity_summary_collection_id ON procuringEntity_summary (collection_id);

