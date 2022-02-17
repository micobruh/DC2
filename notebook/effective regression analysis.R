df <- read.csv("C:\\Users\\20201242\\Documents\\Year 2\\Q3\\Data Challenge 2\\effective_regression.csv")
lm1 <- lm(Crime_Amount ~ Deployed_Amount, data = df)
summary(lm1)
plot(df$Deployed_Amount, df$Crime_Amount, col = "blue",
     main = "Police Effectiveness Regression", xlab = "Deployed Amount", ylab = "Crime Amount")
abline(lm1)