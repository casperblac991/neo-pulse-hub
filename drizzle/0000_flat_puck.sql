CREATE TABLE `automation_tasks` (
	`id` int AUTO_INCREMENT NOT NULL,
	`name` varchar(64) NOT NULL,
	`status` enum('running','success','error','pending','disabled') NOT NULL DEFAULT 'pending',
	`lastRun` timestamp,
	`nextRun` timestamp,
	`lastError` text,
	`successCount` int NOT NULL DEFAULT 0,
	`errorCount` int NOT NULL DEFAULT 0,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `automation_tasks_id` PRIMARY KEY(`id`),
	CONSTRAINT `automation_tasks_name_unique` UNIQUE(`name`)
);
--> statement-breakpoint
CREATE TABLE `blog_posts` (
	`id` varchar(64) NOT NULL,
	`title` varchar(255) NOT NULL,
	`language` enum('EN','AR') NOT NULL,
	`productId` varchar(64),
	`content` text,
	`slug` varchar(255),
	`keywords` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `blog_posts_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `execution_logs` (
	`id` int AUTO_INCREMENT NOT NULL,
	`taskId` int NOT NULL,
	`taskName` varchar(64) NOT NULL,
	`status` enum('success','error','warning','info') NOT NULL,
	`message` text,
	`details` text,
	`timestamp` timestamp NOT NULL DEFAULT (now()),
	`duration` int,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `execution_logs_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `products` (
	`id` varchar(64) NOT NULL,
	`title` varchar(255) NOT NULL,
	`price` int,
	`rating` varchar(10),
	`reviews` int,
	`category` varchar(64),
	`image` text,
	`url` text,
	`features` text,
	`descriptions` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `products_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `system_health` (
	`id` int AUTO_INCREMENT NOT NULL,
	`service` varchar(64) NOT NULL,
	`status` enum('online','offline','degraded','unknown') NOT NULL DEFAULT 'unknown',
	`lastCheck` timestamp NOT NULL DEFAULT (now()),
	`details` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `system_health_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `telegram_campaigns` (
	`id` varchar(64) NOT NULL,
	`message` text NOT NULL,
	`status` enum('sent','failed','pending') NOT NULL DEFAULT 'pending',
	`deliveryStatus` enum('delivered','failed','pending') NOT NULL DEFAULT 'pending',
	`timestamp` timestamp NOT NULL DEFAULT (now()),
	`error` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `telegram_campaigns_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `users` (
	`id` int AUTO_INCREMENT NOT NULL,
	`openId` varchar(64) NOT NULL,
	`name` text,
	`email` varchar(320),
	`loginMethod` varchar(64),
	`role` enum('user','admin') NOT NULL DEFAULT 'user',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	`lastSignedIn` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `users_id` PRIMARY KEY(`id`),
	CONSTRAINT `users_openId_unique` UNIQUE(`openId`)
);
