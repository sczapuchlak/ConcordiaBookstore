-- MySQL dump 10.13  Distrib 5.7.17, for Win64 (x86_64)
--
-- Host: localhost    Database: bookexchange
-- ------------------------------------------------------
-- Server version	5.7.19-log

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
-- Table structure for table `book`
--

DROP TABLE IF EXISTS `book`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `book` (
  `BK_ID` int(11) NOT NULL AUTO_INCREMENT,
  `BK_Title` varchar(60) DEFAULT NULL,
  `CRS_ID` varchar(20) DEFAULT NULL,
  `BK_Publisher` varchar(45) DEFAULT NULL,
  `BK_Price` varchar(45) DEFAULT NULL,
  `PHT_ID` int(11) DEFAULT NULL,
  `BK_Sale_Type` varchar(20) DEFAULT NULL,
  `BK_Comment` varchar(100) DEFAULT NULL,
  `BK_ISBN` varchar(15) DEFAULT NULL,
  `BK_Author` varchar(45) DEFAULT NULL,
  `BK_Edition` varchar(20) DEFAULT NULL,
  `BK_Sold` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`BK_ID`),
  UNIQUE KEY `BK_ID_UNIQUE` (`BK_ID`),
  KEY `CRS_ID_idx` (`CRS_ID`),
  KEY `PHT_ID_idx` (`PHT_ID`),
  CONSTRAINT `CRS_ID` FOREIGN KEY (`CRS_ID`) REFERENCES `course` (`CRS_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `PHT_ID` FOREIGN KEY (`PHT_ID`) REFERENCES `photo` (`PHT_ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `book`
--

LOCK TABLES `book` WRITE;
/*!40000 ALTER TABLE `book` DISABLE KEYS */;
INSERT INTO `book` VALUES (6,'Test Book','HWK 100','Blah house publishing',NULL,6,'sell','','1234567890123','Gary','1st',NULL),(13,'Third time\'s the charm!','HWK101','Blah house publishing',NULL,13,'sell','','1234567890123','Eric the Red','1st',NULL),(14,'Final','SPD101','Blah house publishing',NULL,14,'sell','','9876543210','Eric the Red','1st',NULL),(15,'Testy testy!','HWK110','Blah house publishing',NULL,15,'sell','','5432109876','Eric the Red','1st',NULL);
/*!40000 ALTER TABLE `book` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-04-07 16:23:45
