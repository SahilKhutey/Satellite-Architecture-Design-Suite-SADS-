export interface Annotation {
  id: string;
  label: string;
  position: [number, number, number];
}

export class AnnotationSystem {
  private annotations: Map<string, Annotation> = new Map();

  public addAnnotation(id: string, label: string, position: [number, number, number]): void {
    this.annotations.set(id, { id, label, position });
    console.log(`Added annotation label "${label}" at coordinate [${position}]`);
  }

  public getAnnotations(): Annotation[] {
    return Array.from(this.annotations.values());
  }

  public removeAnnotation(id: string): boolean {
    return this.annotations.delete(id);
  }

  public annotate(id: string, text: string): void {
    const existing = this.annotations.get(id);
    if (existing) {
      existing.label = text;
      console.log(`Updated annotation ID "${id}" label to: "${text}"`);
    } else {
      this.addAnnotation(id, text, [0, 0, 0]);
    }
  }
}