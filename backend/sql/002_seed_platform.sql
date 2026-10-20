-- Datos semilla alineados al mock del frontend.
-- Ejecutar DESPUÉS de 001_create_schema.sql, cuando creen la BD.

INSERT INTO users (id, name, email, profile_type, sector, is_admin, active, joined_at) VALUES
('admin1', 'Diego Martínez', 'admin@nexotlab.com', 'company', 'government', TRUE, TRUE, '2026-01-01'),
('user1', 'Camila Rodríguez', 'camila@nexotlab.com', 'entrepreneur', 'agro', FALSE, TRUE, '2026-03-15'),
('u2', 'Luis Bermúdez', 'luis@nexotlab.com', 'researcher', 'fintech', FALSE, TRUE, '2026-04-02'),
('u3', 'María José Ospina', 'maria@nexotlab.com', 'researcher', 'agro', FALSE, TRUE, '2026-04-18'),
('u4', 'Tomás Ávila', 'tomas@nexotlab.com', 'citizen', 'mobility', FALSE, FALSE, '2026-05-10'),
('u5', 'Paula Mendoza', 'paula@nexotlab.com', 'citizen', 'environment', FALSE, TRUE, '2026-06-01'),
('u6', 'Ricardo Soto', 'ricardo@nexotlab.com', 'entrepreneur', 'energy', FALSE, TRUE, '2026-06-15'),
('u7', 'Natalia Torres', 'natalia@nexotlab.com', 'entrepreneur', 'education', FALSE, TRUE, '2026-07-01'),
('u8', 'Andrés Peña', 'andres@nexotlab.com', 'researcher', 'health', FALSE, TRUE, '2026-07-20'),
('u9', 'Valentina Cruz', 'vale@nexotlab.com', 'company', 'fintech', FALSE, TRUE, '2026-08-05'),
('u10', 'Sebastián Mora', 'sebas@nexotlab.com', 'citizen', 'government', FALSE, FALSE, '2026-08-20')
ON CONFLICT (id) DO NOTHING;

INSERT INTO proposals (id, title, category, sector, description, deliverable, author_id, status, current_score, evaluations_count, created_at) VALUES
('p1', 'Sistema de trazabilidad agrícola con blockchain', 'digital-transformation', 'agro', 'Sistema descentralizado de trazabilidad agrícola con blockchain.', 'Prototipo web + API REST + informe de viabilidad.', 'user1', 'good', 4.7, 47, '2026-08-01'),
('p2', 'Marketplace de servicios para microempresarios rurales', 'digital-economy', 'fintech', 'Plataforma que conecta microempresarios rurales con compradores urbanos.', 'App móvil con pagos y soporte offline.', 'u2', 'evaluating', 3.3, 23, '2026-08-10'),
('p3', 'Asistente de IA para diagnóstico de suelos colombianos', 'digital-transformation', 'agro', 'Modelo ML con datos edafológicos de 12 regiones.', 'Modelo ML + API + guía ICA.', 'u3', 'needs-improvement', 2.1, 31, '2026-07-28'),
('p4', 'Red de innovación ciudadana para movilidad sostenible', 'digital-economy', 'mobility', 'Comunidad digital de co-diseño de movilidad sostenible.', 'Portal + guía + piloto en 2 municipios.', 'u4', 'evaluating', 3.6, 18, '2026-08-20')
ON CONFLICT (id) DO NOTHING;
