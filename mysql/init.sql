CREATE TABLE `PessoaFisica`(
    `cpf` VARCHAR(16) NOT NULL,
    `nome` VARCHAR(255) NOT NULL,
    `data_nasc` DATE NOT NULL,
    PRIMARY KEY(`cpf`)
);
CREATE TABLE `CorpoAgua`(
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `nome` VARCHAR(255) NOT NULL,
    `coordenadas` VARCHAR(63) NOT NULL,
    `imagemUrl` VARCHAR(2047) NULL
);
CREATE TABLE `Denuncia`(
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `denunciante` VARCHAR(16) NOT NULL,
    `datahora` DATETIME NOT NULL,
    `corpoReferente` INT UNSIGNED NOT NULL,
    `categoria` ENUM('natural', 'antropico') NOT NULL,
    `severidade` ENUM('leve', 'medio', 'grave') NOT NULL,
    `descricao` TEXT NULL
);
CREATE TABLE `PessoaJuridica`(
    `cnpj` VARCHAR(16) NOT NULL,
    `razaoSocial` VARCHAR(255) NOT NULL,
    `representante` VARCHAR(255) NULL,
    `isOrgaoGovernamental` BOOLEAN NOT NULL,
    PRIMARY KEY(`cnpj`)
);
CREATE TABLE `Relatorio`(
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `entidadeEmissora` VARCHAR(16) NOT NULL,
    `datahora` DATETIME NOT NULL,
    `corpoReferente` INT UNSIGNED NOT NULL,
    `texto` TEXT NOT NULL,
    `pH` FLOAT(53) NULL,
    `indiceBiodiversidade` INT NULL
);
CREATE TABLE `Simulacao`(
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `entidadeEmissora` VARCHAR(16) NOT NULL,
    `corpoReferente` INT UNSIGNED NOT NULL,
    `severidade` ENUM('leve', 'medio', 'grave') NOT NULL,
    `descricao` TEXT NOT NULL
);
CREATE TABLE `Solucao`(
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `entidadeEmissora` VARCHAR(16) NOT NULL,
    `corpoReferente` INT UNSIGNED NOT NULL,
    `orcamento` FLOAT(53) NOT NULL,
    `descricao` TEXT NOT NULL
);
CREATE TABLE `Usuario`(
    `id` VARCHAR(16) NOT NULL,
    `senha` VARCHAR(255) NOT NULL,
    `tipo` ENUM('pf', 'pj') NOT NULL,
    PRIMARY KEY(`id`)
);

ALTER TABLE
    `Denuncia` ADD CONSTRAINT `denuncia_denunciante_foreign` FOREIGN KEY(`denunciante`) REFERENCES `PessoaFisica`(`cpf`);
ALTER TABLE
    `Solucao` ADD CONSTRAINT `solucao_corporeferente_foreign` FOREIGN KEY(`corpoReferente`) REFERENCES `CorpoAgua`(`id`);
ALTER TABLE
    `Solucao` ADD CONSTRAINT `solucao_entidadeemissora_foreign` FOREIGN KEY(`entidadeEmissora`) REFERENCES `PessoaJuridica`(`cnpj`);
ALTER TABLE
    `PessoaFisica` ADD CONSTRAINT `pessoafisica_cpf_foreign` FOREIGN KEY(`cpf`) REFERENCES `Usuario`(`id`);
ALTER TABLE
    `PessoaJuridica` ADD CONSTRAINT `pessoajuridica_cnpj_foreign` FOREIGN KEY(`cnpj`) REFERENCES `Usuario`(`id`);
ALTER TABLE
    `Denuncia` ADD CONSTRAINT `denuncia_corporeferente_foreign` FOREIGN KEY(`corpoReferente`) REFERENCES `CorpoAgua`(`id`);
ALTER TABLE
    `Relatorio` ADD CONSTRAINT `relatorio_entidadeemissora_foreign` FOREIGN KEY(`entidadeEmissora`) REFERENCES `PessoaJuridica`(`cnpj`);
ALTER TABLE
    `Simulacao` ADD CONSTRAINT `simulacao_entidadeemissora_foreign` FOREIGN KEY(`entidadeEmissora`) REFERENCES `PessoaJuridica`(`cnpj`);
ALTER TABLE
    `Simulacao` ADD CONSTRAINT `simulacao_corporeferente_foreign` FOREIGN KEY(`corpoReferente`) REFERENCES `CorpoAgua`(`id`);
ALTER TABLE
    `Relatorio` ADD CONSTRAINT `relatorio_corporeferente_foreign` FOREIGN KEY(`corpoReferente`) REFERENCES `CorpoAgua`(`id`);


-- POPULATE:
INSERT INTO CorpoAgua (`id`, `nome`, `coordenadas`, `imagemUrl`) VALUES
(1, 'Rio Tietê', '-22.126302,-48.754388', 'https://upload.wikimedia.org/wikipedia/commons/1/16/Rio_Tiet%C3%AA_Barra_Bonita_150606_REFON.jpg'),
(2, 'Rio Amazonas', '-3.065229,-59.795789', 'https://s4.static.brasilescola.uol.com.br/be/2022/05/floresta-amazonica-rio-amazonas.jpg'),
(3, 'Rio Iguaçu', '-26.0061431,-51.8780114', 'https://lh5.googleusercontent.com/p/AF1QipOu0Lnr8_gaQ-9RCq2kzkRHWvkYLltSjTxLkQpC=w408-h244-k-no'),
(4, 'Rio Paraná', '-27.0692753,-61.2049704', 'https://lh5.googleusercontent.com/p/AF1QipN2VwqDBOHBaaHAxuDdU5KF6OzYO61KjjYhMU6m=w408-h306-k-no'),
(5, 'Rio Tapajós', '-4.7849043,-59.2670744', 'https://lh5.googleusercontent.com/p/AF1QipOuBh3kqt7enF_ho-PcgwUVrwefhfAl17SzryZI=w408-h306-k-no');

INSERT INTO `Usuario` (`id`, `senha`, `tipo`) VALUES
('12345678901', 'senhaSeguraPF1', 'pf'),
('23456789012', 'senhaSeguraPF2', 'pf'),
('34567890123', 'senhaSeguraPF3', 'pf'),
('12345678000100', 'senhaSeguraPJ1', 'pj'),
('23456789000100', 'senhaSeguraPJ2', 'pj');

INSERT INTO `PessoaFisica` (`cpf`, `nome`, `data_nasc`) VALUES
('12345678901', 'João Silva', '1985-01-01'),
('23456789012', 'Maria Oliveira', '1990-02-10'),
('34567890123', 'Carlos Souza', '1995-03-15');

INSERT INTO `PessoaJuridica` (`cnpj`, `razaoSocial`, `representante`, `isOrgaoGovernamental`) VALUES
('12345678000100', 'Instituto Rios', 'Secretária X', 0),
('23456789000100', 'Secretaria de Meio Ambiente', 'Secretário Y', 1);

INSERT INTO `Denuncia` (`denunciante`, `datahora`, `corpoReferente`, `categoria`, `severidade`, `descricao`) VALUES
('12345678901', '2024-01-01 10:30:00', 1, 'natural', 'leve', 'Pequena alteração nas margens do rio.'),
('23456789012', '2024-01-05 11:00:00', 2, 'antropico', 'medio', 'Despejo de resíduos no lago.'),
('34567890123', '2024-01-10 14:00:00', 3, 'natural', 'grave', 'Poluição evidente na água.'),
('23456789012', '2024-01-12 15:30:00', 4, 'antropico', 'leve', 'Uso indevido das margens.'),
('12345678901', '2024-01-15 16:45:00', 5, 'natural', 'medio', 'Vegetação degradada.');

INSERT INTO `Relatorio` (`entidadeEmissora`, `datahora`, `corpoReferente`, `texto`, `pH`, `indiceBiodiversidade`) VALUES
('12345678000100', '2024-01-02 09:00:00', 1, 'Análise da qualidade da água.', 4.5, 40),
('23456789000100', '2024-01-06 12:00:00', 2, 'Relatório ambiental detalhado.', 6.8, 70),
('23456789000100', '2024-01-11 13:00:00', 3, 'Situação crítica do rio.', 5.5, 50),
('23456789000100', '2024-01-13 14:00:00', 4, 'Análise de preservação do local.', 8.2, 90),
('12345678000100', '2024-01-16 15:00:00', 5, 'Relatório de preservação ambiental.', 7.0, 75);

INSERT INTO `Simulacao` (`entidadeEmissora`, `corpoReferente`, `severidade`, `descricao`) VALUES
('12345678000100', 1, 'medio', 'Simulação de impacto médio no Rio Tietê.'),
('23456789000100', 2, 'leve', 'Simulação de impacto leve no Rio Amazonas.'),
('12345678000100', 3, 'grave', 'Simulação de impacto grave no Rio Iguaçu.'),
('12345678000100', 4, 'medio', 'Simulação de impacto médio no Rio Paraná.'),
('23456789000100', 5, 'leve', 'Simulação de impacto leve no Rio Tapajós.');

INSERT INTO `Solucao` (`entidadeEmissora`, `corpoReferente`, `orcamento`, `descricao`) VALUES
('12345678000100', 1, 500000.00, 'Projeto de recuperação ambiental do Rio Tietê.'),
('23456789000100', 2, 300000.00, 'Plano de tratamento do Rio Amazonas.'),
('12345678000100', 3, 1000000.00, 'Solução emergencial para o Rio Iguaçu.'),
('23456789000100', 4, 750000.00, 'Projeto de revitalização do Rio Paraná.'),
('23456789000100', 5, 250000.00, 'Plano de controle da qualidade da água do Rio Tapajós.');