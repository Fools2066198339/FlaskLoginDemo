/*
 Navicat Premium Data Transfer

 Source Server         : Localhost
 Source Server Type    : MySQL
 Source Server Version : 50540
 Source Host           : localhost:3306
 Source Schema         : face_login_system

 Target Server Type    : MySQL
 Target Server Version : 50540
 File Encoding         : 65001

 Date: 03/07/2021 17:08:42
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户的ID',
  `username` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '用户的用户名',
  `password` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '用户密码原文拼接盐值后的哈希值',
  `salt` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '用户盐值，即随机生成的字符串',
  `face_img` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '用户基准图片的绝对路径',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `unique_id`(`id`) USING BTREE COMMENT 'id的唯一性索性，不允许存在两个相同的id值',
  UNIQUE INDEX `unique_username`(`username`) USING BTREE COMMENT 'username的唯一性索引，不允许存在两个相同的用户名'
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;

SET FOREIGN_KEY_CHECKS = 1;
