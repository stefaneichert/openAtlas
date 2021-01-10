-- Upgrade 5.6.0 to 5.7.0
-- Be sure to backup the database and read the upgrade notes before executing this!

BEGIN;

-- #1292: Reference systems - add new structure and data
CREATE TABLE web.reference_system (
    entity_id integer NOT NULL,
    name text NOT NULL,
    resolver_url text,
    website_url text,
    precision_default_id integer,
    identifier_example text,
    system boolean DEFAULT false NOT NULL,
    created timestamp without time zone,
    modified timestamp without time zone DEFAULT now() NOT NULL
);

ALTER TABLE web.reference_system OWNER TO openatlas;
COMMENT ON COLUMN web.reference_system.system IS 'True if integrated in the application. Can not be deleted or renamed in the UI.'
ALTER TABLE ONLY web.reference_system ADD CONSTRAINT reference_system_name_key UNIQUE (name);
ALTER TABLE ONLY web.reference_system ADD CONSTRAINT reference_system_pkey PRIMARY KEY (entity_id);
CREATE TRIGGER update_modified BEFORE UPDATE ON web.reference_system FOR EACH ROW EXECUTE PROCEDURE model.update_modified();
ALTER TABLE ONLY web.reference_system ADD CONSTRAINT reference_system_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES model.entity(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY web.reference_system ADD CONSTRAINT reference_system_precision_default_id_fkey FOREIGN KEY (precision_default_id) REFERENCES model.entity(id) ON UPDATE CASCADE ON DELETE CASCADE;

CREATE TABLE web.reference_system_form (
    id integer NOT NULL,
    reference_system_id integer NOT NULL,
    form_id integer NOT NULL
);
ALTER TABLE web.reference_system_form OWNER TO openatlas;
CREATE SEQUENCE web.reference_system_form_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE web.reference_system_form_id_seq OWNER TO openatlas;
ALTER SEQUENCE web.reference_system_form_id_seq OWNED BY web.reference_system_form.id;
ALTER TABLE ONLY web.reference_system_form ALTER COLUMN id SET DEFAULT nextval('web.reference_system_form_id_seq'::regclass);
ALTER TABLE ONLY web.reference_system_form ADD CONSTRAINT reference_system_form_pkey PRIMARY KEY (id);
ALTER TABLE ONLY web.reference_system_form ADD CONSTRAINT reference_system_form_reference_system_id_form_id_key UNIQUE (reference_system_id, form_id);
ALTER TABLE ONLY web.reference_system_form ADD CONSTRAINT reference_system_form_form_id_fkey FOREIGN KEY (form_id) REFERENCES web.form(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY web.reference_system_form ADD CONSTRAINT reference_system_form_reference_system_id_fkey
    FOREIGN KEY (reference_system_id) REFERENCES web.reference_system(entity_id) ON UPDATE CASCADE ON DELETE CASCADE;

INSERT INTO model.entity (name, class_code) VALUES ('GeoNames', 'E32'), ('Wikidata', 'E32');
INSERT INTO web.reference_system (system, name, entity_id, resolver_url, website_url, identifier_example)
VALUES (true,
        'GeoNames',
        (SELECT id FROM model.entity WHERE name = 'GeoNames' AND class_code = 'E32'),
        'https://www.geonames.org/',
        'https://www.geonames.org/',
        '1234567'),
       (true,
        'Wikidata',
        (SELECT id FROM model.entity WHERE name = 'Wikidata' AND class_code = 'E32'),
        'https://www.wikidata.org/entity/',
        'https://www.wikidata.org',
        'Q123');
INSERT INTO web.reference_system_form (reference_system_id, form_id) VALUES
((SELECT entity_id FROM web.reference_system WHERE name='GeoNames'), (SELECT id FROM web.form WHERE name='Place')),
((SELECT entity_id FROM web.reference_system WHERE name='Wikidata'), (SELECT id FROM web.form WHERE name='Place')),
((SELECT entity_id FROM web.reference_system WHERE name='Wikidata'), (SELECT id FROM web.form WHERE name='Person')),
((SELECT entity_id FROM web.reference_system WHERE name='Wikidata'), (SELECT id FROM web.form WHERE name='Group')),
((SELECT entity_id FROM web.reference_system WHERE name='Wikidata'), (SELECT id FROM web.form WHERE name='Legal Body')),
((SELECT entity_id FROM web.reference_system WHERE name='Wikidata'), (SELECT id FROM web.form WHERE name='Event')),
((SELECT entity_id FROM web.reference_system WHERE name='Wikidata'), (SELECT id FROM web.form WHERE name='Feature')),
((SELECT entity_id FROM web.reference_system WHERE name='Wikidata'), (SELECT id FROM web.form WHERE name='Stratigraphic Unit')),
((SELECT entity_id FROM web.reference_system WHERE name='Wikidata'), (SELECT id FROM web.form WHERE name='Find'));

-- #1292: Reference systems - remove former reference systems entries
DELETE FROM web.settings WHERE name in ('geonames_url', 'module_geonames', 'module_wikidata');
DELETE FROM web.user_settings WHERE name in ('module_geonames', 'module_wikidata');

COMMIT;
