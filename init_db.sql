CREATE DATABASE `test`;
USE `test`;
CREATE TABLE `user` (`id` int(11) NOT NULL AUTO_INCREMENT, `username` varchar(40) NOT NULL DEFAULT '', PRIMARY KEY (`id`), UNIQUE KEY `username` (`username`)) ENGINE=InnoDB;
INSERT INTO `user` (`id`, `username`) VALUES (1,'woko'), (2,'liu');