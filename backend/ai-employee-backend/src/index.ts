import express from "express";
import cors from "cors";
import helmet from "helmet";
import { ENV } from "./config/env";
import { requestLogger } from "./middleware/logger.middleware";
import { errorHandler } from "./middleware/error-handler.middleware";
import { authRoutes } from "./modules/auth/auth.routes";
import { aiRoutes } from "./modules/ai-orchestrator/ai.routes";

const app = express();

app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(requestLogger);

app.use("/api/auth", authRoutes);
app.use("/api/ai", aiRoutes);

app.use(errorHandler);

app.listen(ENV.PORT, () => {
  console.log(`Server running on port ${ENV.PORT}`);
});
