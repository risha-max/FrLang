import type { Curriculum, ProgressSummary } from "../api";

export function isLessonCompleted(
  lessonsState: ProgressSummary["lessons"] | undefined,
  lessonId: string,
): boolean {
  return lessonsState?.[lessonId]?.status === "completed";
}

export function isModuleComplete(
  module: Curriculum["modules"][number],
  lessonsState: ProgressSummary["lessons"] | undefined,
): boolean {
  return module.lessons.every((lesson) =>
    isLessonCompleted(lessonsState, lesson.id),
  );
}

export function isModuleUnlocked(
  modules: Curriculum["modules"],
  moduleIndex: number,
  lessonsState: ProgressSummary["lessons"] | undefined,
): boolean {
  if (moduleIndex <= 0) {
    return true;
  }
  return isModuleComplete(modules[moduleIndex - 1], lessonsState);
}

export function isLessonUnlocked(
  curriculum: Curriculum | undefined,
  lessonId: string,
  lessonsState: ProgressSummary["lessons"] | undefined,
): boolean {
  const modules = curriculum?.modules ?? [];
  for (let moduleIndex = 0; moduleIndex < modules.length; moduleIndex += 1) {
    const module = modules[moduleIndex];
    const lessonIndex = module.lessons.findIndex((lesson) => lesson.id === lessonId);
    if (lessonIndex < 0) {
      continue;
    }
    if (!isModuleUnlocked(modules, moduleIndex, lessonsState)) {
      return false;
    }
    for (let i = 0; i < lessonIndex; i += 1) {
      if (!isLessonCompleted(lessonsState, module.lessons[i].id)) {
        return false;
      }
    }
    return true;
  }
  return false;
}
