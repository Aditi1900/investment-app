import { useState, useRef, useEffect } from "react";

const parseNum = (v) => parseFloat(String(v).replace(/[^0-9.]/g, "")) || 0;

export function useAnimatedNumber(target, duration = 600) {
    const [display, setDisplay] = useState(null);
    const prevRef = useRef(null);
    const animRef = useRef(null);
    const hasLoadedRef = useRef(false);

    useEffect(() => {
        if (target === null || target === undefined) return;
        const nextNum = typeof target === "number" ? target : parseNum(target);

        if (!hasLoadedRef.current) {
            hasLoadedRef.current = true;
            prevRef.current = nextNum;
            setDisplay(nextNum);
            return;
        }

        const prevNum = prevRef.current ?? nextNum;
        if (prevNum === nextNum) return;

        const start = performance.now();
        let frame = 0;
        const animate = (now) => {
            const t = Math.min((now - start) / duration, 1);
            frame++;
            if (frame % 2 === 0 || t === 1) setDisplay(prevNum + (nextNum - prevNum) * t);
            if (t < 1) animRef.current = requestAnimationFrame(animate);
            else prevRef.current = nextNum;
        };

        if (animRef.current) cancelAnimationFrame(animRef.current);
        animRef.current = requestAnimationFrame(animate);
        return () => { if (animRef.current) cancelAnimationFrame(animRef.current); };
    }, [target, duration]);

    return display;
}

export const parseNum2 = parseNum;
