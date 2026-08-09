import { Router } from "express";
import { AiController } from "./ai.controller";
import { authenticateJwt } from "../../middleware/auth.middleware";

const router = Router();

router.post("/process", authenticateJwt, AiController.processPrompt);

export const aiRoutes = router;
