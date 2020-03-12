CREATE TABLE stg_XXXX_salesvision_merge_rules_abridged
AS
    WITH RECURSIVE mrg(invalid_value, valid_value, rank) 
    AS (
        SELECT 
            verb.invalid_value as inv,
            verb.valid_value as val, 1 as rank,
            verb.entity_type_id, 
            verb.sf_invalid, 
            verb.sf_valid, 
            verb.sv_invalid, 
            verb.sv_valid, 
            verb.conf_date, 
            verb.created_at
    FROM stg_XXXX_salesvision_merge_rules verb
    UNION ALL
    SELECT 
        mrg.invalid_value, 
        m.valid_value, 
        mrg.rank + 1,
        m.entity_type_id,
        mrg.sf_invalid, 
        m.sf_valid,
        mrg.sv_invalid,
        m.sv_valid,
        m.conf_date,
        m.created_at
    FROM stg_XXXX_salesvision_merge_rules m
    JOIN mrg ON mrg.valid_value = m.invalid_value
    )
    SELECT *
    FROM mrg
GO
CREATE TABLE stg_XXXX_salesvision_merge_rules_max_rank AS
    SELECT v.*
        FROM stg_XXXX_salesvision_merge_rules_abridged v
        JOIN (
                SELECT invalid_value, max(rank) max_rank
                FROM stg_XXXX_salesvision_merge_rules_abridged
                GROUP BY invalid_value
            ) s
        ON s.invalid_value = v.invalid_value
            AND s.max_rank = v.rank
GO
// determines the type of merge, with metadata
// Merge types:
//  - partial/full SF
//  - partial/full SV
//  - full merge
CREATE TABLE stg_XXXX_salesvision_merge_rules_verbose
AS
    WITH mrg_cte AS (
        SELECT 
            mrg.entity_type_id, 
            mrg.invalid_value, 
            mrg.valid_value, 
            mrg.sf_invalid, 
            mrg.sf_valid, 
            sf_inv.salesforce_id as sf_sf_invalid, 
            sf_val.salesforce_id as sf_sf_valid, 
            mrg.sv_invalid, 
            mrg.sv_valid, 
            mrg.conf_date, 
            mrg.created_at,
            'f_both' as merge_rule, 
            mrg.rank
        FROM stg_XXXX_salesvision_merge_rules_max_rank mrg
        LEFT JOIN sf_entity_entity sf_val ON mrg.valid_value = sf_val.persistence_id
        LEFT JOIN sf_entity_entity sf_inv ON mrg.invalid_value = sf_inv.persistence_id
        WHERE sf_inv.salesforce_id != sf_val.salesforce_id
        UNION
        SELECT 
            mrg.entity_type_id, 
            mrg.invalid_value, 
            mrg.valid_value, 
            mrg.sf_invalid, 
            mrg.sf_valid, 
            sf_inv.salesforce_id as sf_sf_invalid, 
            sf_val.salesforce_id as sf_sf_valid, 
            mrg.sv_invalid, 
            mrg.sv_valid, 
            mrg.conf_date, 
            mrg.created_at,
            'f_sv' as merge_rule, 
            mrg.rank
        FROM stg_XXXX_salesvision_merge_rules_max_rank mrg
        LEFT JOIN sf_entity_entity sf_val ON mrg.valid_value = sf_val.persistence_id
        LEFT JOIN sf_entity_entity sf_inv ON mrg.invalid_value = sf_inv.persistence_id
        WHERE sf_inv.salesforce_id is NULL AND sf_val.salesforce_id is NULL
        UNION
        SELECT 
            mrg.entity_type_id, 
            mrg.invalid_value, 
            mrg.valid_value, 
            mrg.sf_invalid, 
            mrg.sf_valid, 
            sf_inv.salesforce_id as sf_sf_invalid, 
            sf_val.salesforce_id as sf_sf_valid, 
            mrg.sv_invalid, 
            mrg.sv_valid, 
            mrg.conf_date, 
            mrg.created_at,
            'f_sf' as merge_rule, 
            mrg.rank
        FROM stg_XXXX_salesvision_merge_rules_max_rank mrg
        LEFT JOIN sf_entity_entity sf_val ON mrg.valid_value = sf_val.persistence_id
        LEFT JOIN sf_entity_entity sf_inv ON mrg.invalid_value = sf_inv.persistence_id
        WHERE sv_invalid is NULL AND sv_valid is NULL
        UNION
        SELECT 
            mrg.entity_type_id, 
            mrg.invalid_value, 
            mrg.valid_value, 
            mrg.sf_invalid, 
            mrg.sf_valid, 
            sf_inv.salesforce_id as sf_sf_invalid, 
            sf_val.salesforce_id as sf_sf_valid, 
            mrg.sv_invalid, 
            mrg.sv_valid, 
            mrg.conf_date, 
            mrg.created_at,
            'p_sf' as merge_rule, 
            mrg.rank -- winner p_id is in salesforce
        FROM stg_XXXX_salesvision_merge_rules_max_rank mrg
        LEFT JOIN sf_entity_entity sf_val ON mrg.valid_value = sf_val.persistence_id
        LEFT JOIN sf_entity_entity sf_inv ON mrg.invalid_value = sf_inv.persistence_id
        WHERE sf_val.salesforce_id IS NOT NULL and sf_inv.salesforce_id is NULL
        UNION
        SELECT 
            mrg.entity_type_id, 
            mrg.invalid_value, 
            mrg.valid_value, 
            mrg.sf_invalid, 
            mrg.sf_valid, 
            sf_inv.salesforce_id as sf_sf_invalid, 
            sf_val.salesforce_id as sf_sf_valid, 
            mrg.sv_invalid, 
            mrg.sv_valid, 
            mrg.conf_date, 
            mrg.created_at,
            'p_sv' as merge_rule, 
            mrg.rank -- winner p_id is in salesvision
        FROM stg_XXXX_salesvision_merge_rules_max_rank mrg
        LEFT JOIN sf_entity_entity sf_val ON mrg.valid_value = sf_val.persistence_id
        LEFT JOIN sf_entity_entity sf_inv ON mrg.invalid_value = sf_inv.persistence_id
        WHERE sf_val.salesforce_id is NULL and sf_inv.salesforce_id is NOT NULL
        )
    SELECT v.*
    FROM mrg_cte v
    JOIN (
            SELECT invalid_value, 
            max(rank) max_rank
            FROM mrg_cte
            GROUP BY invalid_value
        ) s
    ON s.invalid_value = v.invalid_value
        AND s.max_rank = v.rank
GO
// all entites affected by above merges
// valid/invalid parent: whether record is winner/loser of merge
// valid/invalid child: winner/loser of parent
// commonly called "merge master"
CREATE TABLE stg_XXXX_merge_master_affected_entities
AS 
    SELECT  inv_ents.persistence_id as root_id,
        'invalid_parent' as ent_type,
        'invalid' as val_type, 
        merge_rule, rank,
        NULL as parent_status,
        CASE WHEN inv_ents.ended_at IS NULL THEN 'alive' ELSE 'dead' END as self_status,
        inv_ents.*
    FROM stg_XXXX_salesvision_merge_rules_verbose verb
    JOIN stg_XXXX_entity inv_ents
        ON inv_ents.persistence_id = verb.invalid_value
    UNION 
    SELECT  val_ents.persistence_id as root_id,
            'valid_parent' as ent_type,  
            'valid' as val_type,
            merge_rule, rank,
            NULL as parent_status,
            CASE WHEN val_ents.ended_at IS NULL THEN 'alive' ELSE 'dead' END as self_status,
            val_ents.*
    FROM stg_XXXX_salesvision_merge_rules_verbose verb
    JOIN stg_XXXX_entity val_ents
        ON val_ents.persistence_id = verb.valid_value
    UNION
    SELECT  inv_ents.persistence_id as root_id,
            'inv_child' as ent_type,      
            'invalid' as val_type,
            merge_rule, rank,
            CASE WHEN inv_ents.ended_at IS NULL THEN 'alive' ELSE 'dead' END as parent_status,
            CASE WHEN inv_child.ended_at IS NULL THEN 'alive' ELSE 'dead' END as self_status,
            inv_child.*
    FROM stg_XXXX_salesvision_merge_rules_verbose verb
    JOIN stg_XXXX_entity inv_ents
        ON inv_ents.persistence_id = verb.invalid_value
    JOIN stg_XXXX_entity inv_child
        ON inv_ents.entity_id = inv_child.parent_id
    UNION 
    SELECT  val_ents.persistence_id as root_id,
            'val_child' as ent_type, 
            'valid' as val_type,
            merge_rule, rank,
            CASE WHEN val_ents.ended_at IS NULL THEN 'alive' ELSE 'dead' END as parent_status,
            CASE WHEN val_child.ended_at IS NULL THEN 'alive' ELSE 'dead' END as self_status,
            val_child.*
    FROM stg_XXXX_salesvision_merge_rules_verbose verb
    JOIN stg_XXXX_entity val_ents
        ON val_ents.persistence_id = verb.valid_value
    JOIN stg_XXXX_entity val_child
        ON val_ents.entity_id = val_child.parent_id
    UNION
    SELECT  val_ents.persistence_id as root_id,
            'sf_inv_child' as ent_type, 
            'invalid' as val_type,
            merge_rule, rank,
            CASE WHEN cm_parent.ended_at IS NULL THEN 'alive' ELSE 'dead' END as parent_status,
            CASE WHEN cm_child.ended_at IS NULL THEN 'alive' ELSE 'dead' END as self_status,
            cm_child.*
    FROM stg_XXXX_salesvision_merge_rules_verbose verb
    JOIN stg_XXXX_entity val_ents
        ON val_ents.persistence_id = verb.valid_value
    LEFT JOIN stg_XXXX_entity sf_par
        ON val_ents.salesforce_id = sf_par.salesforce_id
    LEFT JOIN stg_XXXX_entity sf_child
        ON sf_par.entity_id = sf_child.parent_id
    LEFT JOIN stg_XXXX_entity cm_child
        ON cm_child.salesforce_id = sf_child.salesforce_id
    LEFT JOIN stg_XXXX_entity cm_parent
        ON cm_child.parent_id = cm_parent.entity_id
GO
// OLD
CREATE TABLE stg_XXXX_bad_roots 
AS
    SELECT DISTINCT root_id
    FROM
    (
        SELECT 
            sf_p.salesforce_id,
            -- Merge Assumptions
            --- All children of merges should be reassigned
            CASE WHEN self_status = 'alive' AND parent_status = 'dead' THEN TRUE ELSE FALSE END as error_ended_parent,
            -- SalesForce Assumptions
            --- SalesForce ID in CM must exist in CM
            CASE WHEN self_status = 'alive' AND sf.salesforce_id IS NULL AND cm.salesforce_id IS NOT NULL THEN TRUE ELSE FALSE END as error_sf_id_missing,
            --- If the persistence_id exists in both systems. CM needs a SF ID
            CASE WHEN self_status = 'alive' AND sf_p.salesforce_id IS NOT NULL AND cm.salesforce_id IS NULL THEN TRUE ELSE FALSE END as error_dropped_sf_id,
            cm.*
        FROM stg_XXXX_merge_master_affected_entities cm
        LEFT JOIN sf_entity_entity sf
            ON sf.salesforce_id = cm.salesforce_id
            AND cm.salesforce_id IS NOT NULL
        LEFT JOIN sf_entity_entity sf_p
            ON cm.persistence_id = sf_p.persistence_id
    ) s
    JOIN stg_XXXX_entity e
        ON e.entity_id = s.parent_id
    LEFT JOIN stg_XXXX_salesvision_merge_rules_verbose v
        ON v.valid_value = e.persistence_id
    LEFT JOIN stg_XXXX_salesvision_merge_exceptions exc
        ON exc.persistence_id = e.persistence_id
    WHERE error_sf_id_missing = TRUE
          OR error_ended_parent = TRUE
          OR error_dropped_sf_id = TRUE
GO
replace XXXX with the current stg switch, makes it easy for find/replace (edited) 
