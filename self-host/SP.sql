-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Feb 09, 2023 at 11:24 PM
-- Server version: 10.5.17-MariaDB
-- PHP Version: 7.2.24

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `s8636_MainDB`
--

-- --------------------------------------------------------

--
-- Table structure for table `SP`
--

CREATE TABLE `SP` (
  `id` int(5) UNSIGNED NOT NULL,
  `smashed` mediumint(9) DEFAULT NULL,
  `passed` mediumint(9) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `USERS`
--

CREATE TABLE `USERS` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `smashed` int(7) UNSIGNED DEFAULT 0,
  `passed` int(7) UNSIGNED DEFAULT 0,
  `favPoke` int(5) UNSIGNED NOT NULL DEFAULT 1,
  `showPrev` tinyint(1) DEFAULT 0,
  `prevTime` int(2) UNSIGNED DEFAULT 10
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `SP`
--
ALTER TABLE `SP`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `USERS`
--
ALTER TABLE `USERS`
  ADD PRIMARY KEY (`id`),
  ADD KEY `favPoke` (`favPoke`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `USERS`
--
ALTER TABLE `USERS`
  ADD CONSTRAINT `USERS_ibfk_1` FOREIGN KEY (`favPoke`) REFERENCES `SP` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
