-- MySQL dump 10.13  Distrib 5.5.22, for debian-linux-gnu (i686)
--
-- Host: localhost    Database: miniimdb
-- ------------------------------------------------------
-- Server version	5.5.22-0ubuntu1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `downloads`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `downloads` (
  `iddownload` mediumint(10) unsigned NOT NULL AUTO_INCREMENT,
  `type` enum('movies','episodes') NOT NULL,
  `fkid` mediumint(10) unsigned NOT NULL,
  `tags` varchar(240) NOT NULL,
  `downloading` bit(1) DEFAULT b'0',
  PRIMARY KEY (`iddownload`),
  UNIQUE KEY `iddownload` (`iddownload`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `episodes`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `episodes` (
  `idepisode` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idshow` mediumint(7) unsigned NOT NULL,
  `season` tinyint(3) unsigned NOT NULL,
  `episode` smallint(6) unsigned NOT NULL,
  `have` bit(1) DEFAULT b'0',
  PRIMARY KEY (`idepisode`),
  UNIQUE KEY `idepisode` (`idepisode`),
  UNIQUE KEY `idshow` (`idshow`,`season`,`episode`)
) ENGINE=MyISAM AUTO_INCREMENT=963031 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `movies`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `movies` (
  `idmovie` mediumint(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(300) NOT NULL,
  `year` varchar(9) NOT NULL,
  `have` bit(1) DEFAULT b'0',
  `special` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`idmovie`),
  UNIQUE KEY `idmovie` (`idmovie`),
  UNIQUE KEY `name` (`name`,`year`,`special`)
) ENGINE=MyISAM AUTO_INCREMENT=818074 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `shows`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `shows` (
  `idshow` mediumint(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(300) NOT NULL,
  `year` varchar(36) NOT NULL,
  `follow` bit(1) DEFAULT b'0',
  `special` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`idshow`),
  UNIQUE KEY `idshow` (`idshow`),
  UNIQUE KEY `name` (`name`,`year`,`special`)
) ENGINE=MyISAM AUTO_INCREMENT=115994 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2012-06-05 18:05:32
