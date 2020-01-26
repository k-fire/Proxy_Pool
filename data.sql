# Host: localhost  (Version: 5.5.53)
# Date: 2020-01-22 22:33:17
# Generator: MySQL-Front 5.3  (Build 4.234)

/*!40101 SET NAMES utf8 */;

#
# Structure for table "all_proxy"
#

DROP TABLE IF EXISTS `all_proxy`;
CREATE TABLE `all_proxy` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `proxy` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=MyISAM AUTO_INCREMENT=1610 DEFAULT CHARSET=utf8;

#
# Data for table "all_proxy"
#

/*!40000 ALTER TABLE `all_proxy` DISABLE KEYS */;
/*!40000 ALTER TABLE `all_proxy` ENABLE KEYS */;

#
# Structure for table "valid_proxy"
#

DROP TABLE IF EXISTS `valid_proxy`;
CREATE TABLE `valid_proxy` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `proxy` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=MyISAM AUTO_INCREMENT=295 DEFAULT CHARSET=utf8;

#
# Data for table "valid_proxy"
#

/*!40000 ALTER TABLE `valid_proxy` DISABLE KEYS */;
/*!40000 ALTER TABLE `valid_proxy` ENABLE KEYS */;
