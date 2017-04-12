/*
Navicat MySQL Data Transfer

Source Server         : localhost-amp
Source Server Version : 50716
Source Host           : localhost:3306
Source Database       : sina

Target Server Type    : MYSQL
Target Server Version : 50716
File Encoding         : 65001

Date: 2017-04-13 07:33:51
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for sina
-- ----------------------------
DROP TABLE IF EXISTS `sina`;
CREATE TABLE `sina` (
  `uid` varchar(11) COLLATE utf8_bin DEFAULT NULL,
  `last_content` text COLLATE utf8_bin,
  `tools` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `likes` int(255) DEFAULT NULL,
  `comments` int(255) DEFAULT NULL,
  `transfer` int(255) DEFAULT NULL,
  `public_time` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `emotion` int(11) DEFAULT NULL,
  `update_time` int(11) NOT NULL DEFAULT '0',
  UNIQUE KEY `unique_uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- ----------------------------
-- Table structure for watcher_users
-- ----------------------------
DROP TABLE IF EXISTS `watcher_users`;
CREATE TABLE `watcher_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` varchar(11) COLLATE utf8_bin NOT NULL,
  `email` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_uid` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
