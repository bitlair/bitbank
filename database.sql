-- phpMyAdmin SQL Dump
-- version 3.2.2.1deb1
-- http://www.phpmyadmin.net
--
-- Machine: localhost
-- Genereertijd: 08 Jun 2011 om 10:09
-- Serverversie: 5.1.37
-- PHP-Versie: 5.2.10-2ubuntu6.10

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

--
-- Database: `bitbar`
--

-- --------------------------------------------------------

--
-- Tabelstructuur voor tabel `member`
--

CREATE TABLE IF NOT EXISTS `member` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `barcode` varchar(25) NOT NULL,
  `nick` varchar(255) NOT NULL,
  `balance` decimal(9,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabelstructuur voor tabel `products`
--

CREATE TABLE IF NOT EXISTS `products` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `barcode` varchar(25) NOT NULL,
  `price` decimal(9,2) NOT NULL,
  `member_price` decimal(9,2) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;
