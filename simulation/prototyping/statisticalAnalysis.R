library("ggplot2")
library("reshape2")

## Realized that the 5 sec interval should be a 10 sec interval
## and that the 10 sec interval should be a 20 sec interval.
## Will update variable names accordingly soon

setwd ("~/Documents/code/robotics/simulation/morse/AI_Robots_multiAgent/simulation/results/")

data_full <- read.csv ("simu_full.csv")

data_full_10s <- data_full[data_full$Interval_s == 10, ]
data_full_5s <- data_full[data_full$Interval_s == 5, ]

data_10m_10s <- data_full_10s[data_full_10s$Altitude_m == 10, ]
data_50m_10s <- data_full_10s[data_full_10s$Altitude_m == 50, ]
data_75m_10s <- data_full_10s[data_full_10s$Altitude_m == 75, ]
data_10m_5s <- data_full_5s[data_full_5s$Altitude_m == 10, ]
data_50m_5s <- data_full_5s[data_full_5s$Altitude_m == 50, ]
data_75m_5s <- data_full_5s[data_full_5s$Altitude_m == 75, ]


getStats <- function (df) {
  mean <- mean (df$ProportionInView)
  sd <- sd (df$ProportionInView)
  median <- median (df$ProportionInView)
  
  #mean <- format(mean, scientific = TRUE, digits = 3)
  #sd <- format(sd, scientific = TRUE, digits = 3)
  #median <- format(median, scientific = TRUE, digits = 3)
  
  stats <- cbind.data.frame(mean, sd, median)
  colnames (stats) <- c ("Mean", "SD", "Median")
  stats
}

getStatsFormat <- function (df) {
  altitude_m = df[1,]$Altitude_m
  interval_s = df[1,]$Interval_s
  usingWaypoints = df[1,]$UsingWaypoints
  stats <- getStats (df)
  statsFormat <- cbind.data.frame(usingWaypoints, interval_s, altitude_m, stats)
  colnames (statsFormat)[1:3] <- c ("UsingWaypoints", "Interval_s", "Altitude_m")
  statsFormat
}


stats_10m_10s_W <- getStatsFormat (data_10m_10s [data_10m_10s $UsingWaypoints == TRUE,  ])
stats_50m_10s_W <- getStatsFormat (data_50m_10s [data_50m_10s $UsingWaypoints == TRUE,  ])
stats_75m_10s_W <- getStatsFormat (data_75m_10s [data_75m_10s $UsingWaypoints == TRUE,  ])
stats_10m_5s_W  <- getStatsFormat (data_10m_5s  [data_10m_5s  $UsingWaypoints == TRUE,  ])
stats_50m_5s_W  <- getStatsFormat (data_50m_5s  [data_50m_5s  $UsingWaypoints == TRUE,  ])
stats_75m_5s_W  <- getStatsFormat (data_75m_5s  [data_75m_5s  $UsingWaypoints == TRUE,  ])
stats_10m_10s_N <- getStatsFormat (data_10m_10s [data_10m_10s $UsingWaypoints == FALSE, ])
stats_50m_10s_N <- getStatsFormat (data_50m_10s [data_50m_10s $UsingWaypoints == FALSE, ])
stats_75m_10s_N <- getStatsFormat (data_75m_10s [data_75m_10s $UsingWaypoints == FALSE, ])
stats_10m_5s_N  <- getStatsFormat (data_10m_5s  [data_10m_5s  $UsingWaypoints == FALSE, ])
stats_50m_5s_N  <- getStatsFormat (data_50m_5s  [data_50m_5s  $UsingWaypoints == FALSE, ])
stats_75m_5s_N  <- getStatsFormat (data_75m_5s  [data_75m_5s  $UsingWaypoints == FALSE, ])


stats_full <- rbind.data.frame(stats_10m_10s_W, stats_10m_10s_N, stats_50m_10s_W, stats_50m_10s_N, stats_75m_10s_W, stats_75m_10s_N, 
                 stats_10m_5s_W, stats_10m_5s_N, stats_50m_5s_W, stats_50m_5s_N, stats_75m_5s_W, stats_75m_5s_N)
write.csv (x = stats_full, "simu_full_stats.csv", quote = FALSE)

# Compare the mean proportionss between with and without waypoints
means_W <- stats_full[stats_full$UsingWaypoints == TRUE, ]$Mean
means_N <- stats_full[stats_full$UsingWaypoints == FALSE, ]$Mean
meansDifference <- means_W - means_N
meansDifference_10s <- meansDifference[1:3]
meansDifference_5s <- meansDifference[4:6]
descriptions <- c ("10", "50", "75")
meansTbl <- cbind.data.frame (descriptions, meansDifference_5s, meansDifference_10s)
colnames (meansTbl) = c ("Altitude", "10", "20")
meansTbl <- melt (meansTbl, id.vars = "Altitude")
#
ggplot (meansTbl, aes (Altitude, value, fill = variable)) + 
  geom_col (position="dodge") +
  xlab ("Altitude (m)") + 
  ylab ("Difference between means with and without waypoint information") + 
  guides(fill=guide_legend(title="Message\nInterval (s)"))



# Compare the proportions
props_W <- data_full[data_full$UsingWaypoints == TRUE, ]$ProportionInView
props_N <- data_full[data_full$UsingWaypoints == FALSE, ]$ProportionInView
props_tbl <- cbind.data.frame (props_W, props_N)
colnames (props_tbl) = c ("WithWaypoints", "WithoutWaypoints")
# Plot
ggplot (props_tbl, aes(x = props_N, y = props_W)) + geom_point () + geom_smooth (method = loess, se = FALSE) +
  xlab ("Proportion targets kept\nin view without waypoints") +
  ylab ("Proportion targets kept in view with waypoints") 



# Paired T-Test

getPaired_Ttest <- function (df) {
  ProportionsWithWaypoints <- df[df$UsingWaypoints == TRUE, ]$ProportionInView
  ProportionsSansWaypoints <- df[df$UsingWaypoints == FALSE, ]$ProportionInView
  t.test(ProportionsWithWaypoints, ProportionsSansWaypoints, paired=TRUE)
}

ProportionsWithWaypoints <- data_full[data_full$UsingWaypoints == TRUE, ]$ProportionInView
ProportionsSansWaypoints <- data_full[data_full$UsingWaypoints == FALSE, ]$ProportionInView

T_full    <- getPaired_Ttest (data_full)
T_10m_10s <- getPaired_Ttest (data_10m_10s)
T_50m_10s <- getPaired_Ttest (data_50m_10s)
T_75m_10s <- getPaired_Ttest (data_75m_10s)
T_10m_5s  <- getPaired_Ttest (data_10m_5s)
T_50m_5s  <- getPaired_Ttest (data_50m_5s)
T_75m_5s  <- getPaired_Ttest (data_75m_5s)


row_full    <- c ("All", "All", format (T_full$statistic, scientific = TRUE, digits = 3), T_full$parameter, format (T_full$p.value, scientific = TRUE, digits = 3))
row_10m_10s <- c ("10", "10", format (T_10m_10s$statistic, scientific = TRUE, digits = 3), T_10m_10s$parameter, format (T_10m_10s$p.value, scientific = TRUE, digits = 3))
row_50m_10s <- c ("50", "10", format (T_50m_10s$statistic, scientific = TRUE, digits = 3), T_50m_10s$parameter, format (T_50m_10s$p.value, scientific = TRUE, digits = 3))
row_75m_10s <- c ("75", "10", format (T_75m_10s$statistic, scientific = TRUE, digits = 3), T_75m_10s$parameter, format (T_75m_10s$p.value, scientific = TRUE, digits = 3))
row_10m_5s  <- c ("10", "5", format (T_10m_5s$statistic, scientific = TRUE, digits = 3),  T_10m_5s$parameter,  format (T_10m_5s$p.value, scientific = TRUE, digits = 3))
row_50m_5s  <- c ("50", "5", format (T_50m_5s$statistic, scientific = TRUE, digits = 3),  T_50m_5s$parameter,  format (T_50m_5s$p.value, scientific = TRUE, digits = 3))
row_75m_5s  <- c ("75", "5", format (T_75m_5s$statistic, scientific = TRUE, digits = 3),  T_75m_5s$parameter,  format (T_75m_5s$p.value, scientific = TRUE, digits = 3))

T_tbl <- rbind.data.frame(row_10m_5s, row_50m_5s, row_75m_5s, row_10m_10s, row_50m_10s, row_75m_10s, row_full)
colnames (T_tbl) <- c ("Altitude_m", "Interval_s", "T-stat", "DF", "P-value")
write.csv (x = T_tbl, "simu_full_T_table.csv", quote = FALSE)



# Repositions

RepostionsWithWaypoints <- data_full[data_full$UsingWaypoints == TRUE, ]$NumRepositions
RepositionsSansWaypoints <- data_full[data_full$UsingWaypoints == FALSE, ]$NumRepositions

RepostionsWithWaypoints - RepositionsSansWaypoints

