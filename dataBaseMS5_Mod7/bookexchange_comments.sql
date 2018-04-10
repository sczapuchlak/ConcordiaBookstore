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
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comments` (
  `COM_ID` int(11) NOT NULL AUTO_INCREMENT,
  `COM_Auth` varchar(100) DEFAULT NULL,
  `COM_Date` date DEFAULT NULL,
  `COM_Body` varchar(500) DEFAULT NULL,
  `LST_ID` int(11) DEFAULT NULL,
  `COM_USER_ID` int(11) DEFAULT NULL,
  PRIMARY KEY (`COM_ID`),
  UNIQUE KEY `COM_ID_UNIQUE` (`COM_ID`),
  KEY `LST_ID_idx` (`LST_ID`),
  KEY `USER_Email` (`COM_ID`,`COM_Auth`,`COM_Date`,`COM_Body`,`LST_ID`),
  KEY `COM_USER_ID_idx` (`COM_USER_ID`),
  CONSTRAINT `COM_USER_ID` FOREIGN KEY (`COM_USER_ID`) REFERENCES `user` (`USER_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `LST_ID` FOREIGN KEY (`LST_ID`) REFERENCES `listing` (`LST_ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES (1,'Gary Hall','2018-04-05','One',6,2),(2,'Gary Hall','2018-04-05','Two\r\n',6,2),(3,'Gary Hall','2018-04-05','Three',6,2),(4,'Gary Hall','2018-04-05','Four',6,2),(5,'Gary Hall','2018-04-05','Five',6,2),(6,'Gary Hall','2018-04-05','Six',6,2),(7,'Gary Hall','2018-04-05','Seven',6,2),(8,'Gary Hall','2018-04-05','Eight',6,2),(9,'Gary Hall','2018-04-05','Nine',6,2),(10,'Gary Hall','2018-04-05','Ten',6,2),(11,'Gary Hall','2018-04-05','Eleven',6,2),(12,'Gary Hall','2018-04-05','Twelve',6,2),(13,'Gary Hall','2018-04-05','Thirteen',6,2),(14,'Gary Hall','2018-04-05','Fourteen',6,2),(15,'Gary Hall','2018-04-05','Fifteen',6,2),(16,'Gary Hall','2018-04-05','Sixteen',6,2),(17,'Gary Hall','2018-04-05','Seventeen',6,2),(18,'Gary Hall','2018-04-05','Eighteen',6,2),(19,'Gary Hall','2018-04-05','Nineteen',6,2),(20,'Gary Hall','2018-04-05','Twenty',6,2),(21,'Gary Hall','2018-04-05','Twenty one',6,2);
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
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
