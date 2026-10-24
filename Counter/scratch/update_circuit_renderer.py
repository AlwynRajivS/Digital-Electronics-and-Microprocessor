import os

new_code = '''    // --- Step 8: Logic Circuit Schematic (Exact Textbook Standard: Fig. 8.11 & Fig. 8.13) ---
    function renderStep8(netlist, prob) {
        const svg = document.getElementById('circuitSchematicSvg');
        svg.innerHTML = '';

        const ffList = netlist.flip_flops;
        const ffCount = ffList.length;

        // Dynamic width according to flip flop count
        const width = (ffCount === 2) ? 780 : ((ffCount === 3) ? 980 : 1140);
        const height = 520;
        svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '100%');

        // Color Palette matching high-contrast engineering schematic
        const C_WIRE = '#38bdf8';
        const C_AND = '#c084fc';
        const C_OR = '#ec4899';
        const C_CLK = '#f59e0b';
        const C_VCC = '#10b981';
        const C_GND = '#64748b';
        const C_PROBE = '#10b981';
        const C_FF_BORDER = '#0284c7';
        const C_FF_BG = '#101c33';

        // Defs (Arrowheads, Grid Pattern)
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        defs.innerHTML = `
            <marker id="arrow-up" viewBox="0 0 10 10" refX="5" refY="3" markerWidth="6" markerHeight="6" orient="auto">
                <path d="M 0 10 L 5 0 L 10 10 z" fill="${C_PROBE}"/>
            </marker>
            <marker id="arrow-right-clk" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                <path d="M 0 1 L 9 5 L 0 9 z" fill="${C_CLK}"/>
            </marker>
            <marker id="arrow-right-vcc" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                <path d="M 0 1 L 9 5 L 0 9 z" fill="${C_VCC}"/>
            </marker>
            <pattern id="cad-grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <circle cx="1" cy="1" r="0.7" fill="rgba(255,255,255,0.06)" />
            </pattern>
        `;
        svg.appendChild(defs);

        // CAD Grid Background
        const gridRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        gridRect.setAttribute('width', width);
        gridRect.setAttribute('height', height);
        gridRect.setAttribute('fill', 'url(#cad-grid)');
        svg.appendChild(gridRect);

        // --- Top Horizontal Clock Rail (Fig. 8.11 & 8.13 Hallmark) ---
        const clkY = 72;
        const lastFF_X = (ffCount === 2) ? 580 : ((ffCount === 3) ? 730 : 880);
        const clkLine = createSvgPath(`M 35 ${clkY} L ${lastFF_X + 40} ${clkY}`, C_CLK, 2.5);
        svg.appendChild(clkLine);
        // Arrow on left entering
        const clkTri = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        clkTri.setAttribute('points', `32,${clkY - 6} 44,${clkY} 32,${clkY + 6}`);
        clkTri.setAttribute('fill', C_CLK);
        svg.appendChild(clkTri);
        svg.appendChild(createSvgText(48, clkY - 10, 'Clock input (CLK)', C_CLK, '12px', '700'));

        // --- Top Left VCC (+5V / Logic 1) Line (Fig. 8.11 Hallmark) ---
        const vccY = 112;
        const vccLine = createSvgPath(`M 35 ${vccY} L 85 ${vccY}`, C_VCC, 2.4);
        svg.appendChild(vccLine);
        const vccTri = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        vccTri.setAttribute('points', `32,${vccY - 5} 42,${vccY} 32,${vccY + 5}`);
        vccTri.setAttribute('fill', C_VCC);
        svg.appendChild(vccTri);
        svg.appendChild(createSvgText(46, vccY - 8, 'VCC (Logic 1)', C_VCC, '12px', '700'));

        // --- Flip-Flop Geometry (Left-to-Right: Stage A LSB -> Stage D MSB) ---
        const ffWidth = 110;
        const ffHeight = 160;
        const ffTopY = 135;
        const ffBotY = ffTopY + ffHeight; // 295

        const ffXPositions = (ffCount === 2) ? [240, 560] : ((ffCount === 3) ? [150, 440, 730] : [110, 360, 610, 860]);

        const ffLayout = {};

        ffList.forEach((ff, idx) => {
            const fx = ffXPositions[idx];
            const fy = ffTopY;
            const letter = ff.letter || ff.out_q[1];
            const isLsb = (idx === 0);
            const isMsb = (idx === ffCount - 1);

            ffLayout[ff.out_q] = {
                id: ff.id,
                letter: letter,
                type: ff.type,
                idx: idx,
                isLsb: isLsb,
                isMsb: isMsb,
                x: fx,
                y: fy,
                w: ffWidth,
                h: ffHeight,
                pin_in1: { x: fx, y: fy + 35 },          // J, S, D, T (Y = 170)
                pin_clk: { x: fx, y: fy + 80 },          // CLK in middle (Y = 215)
                pin_in2: { x: fx, y: fy + 125 },         // K, R (Y = 260)
                pin_out_q: { x: fx + ffWidth, y: fy + 35 },     // Q (Y = 170)
                pin_out_q_bar: { x: fx + ffWidth, y: fy + 125 }, // Q' (Y = 260)
                probe_x: fx + ffWidth + 22
            };
        });

        // Draw Flip-Flop Blocks
        Object.values(ffLayout).forEach(ff => {
            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');

            // Main IC Box (Fig. 8.11 style)
            const box = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            box.setAttribute('x', ff.x);
            box.setAttribute('y', ff.y);
            box.setAttribute('width', ff.w);
            box.setAttribute('height', ff.h);
            box.setAttribute('rx', '4');
            box.setAttribute('fill', C_FF_BG);
            box.setAttribute('stroke', C_FF_BORDER);
            box.setAttribute('stroke-width', '2.2');
            g.appendChild(box);

            // Large Bold Center Letter 'A', 'B', 'C', 'D' (Fig. 8.11 hallmark!)
            g.appendChild(createSvgText(ff.x + ff.w / 2, ff.y + ff.h / 2 + 8, ff.letter, '#cbd5e1', '28px', '800', 'middle'));

            // Top Header Label above IC: "Flip-flop A (LSB)"
            const roleSuffix = ff.isLsb ? ' (LSB)' : (ff.isMsb ? ' (MSB)' : '');
            g.appendChild(createSvgText(ff.x + ff.w / 2, ff.y - 10, `Flip-flop ${ff.letter}${roleSuffix}`, '#94a3b8', '12px', '600', 'middle'));

            // Pin Stubs & Labels
            if (ff.type === 'JK') {
                drawInternalPin(g, ff.pin_in1.x, ff.pin_in1.y, `J${ff.letter}`, 'left');
                drawInternalPin(g, ff.pin_in2.x, ff.pin_in2.y, `K${ff.letter}`, 'left');
            } else if (ff.type === 'SR') {
                drawInternalPin(g, ff.pin_in1.x, ff.pin_in1.y, `S${ff.letter}`, 'left');
                drawInternalPin(g, ff.pin_in2.x, ff.pin_in2.y, `R${ff.letter}`, 'left');
            } else if (ff.type === 'D') {
                drawInternalPin(g, ff.pin_in1.x, ff.pin_in1.y, `D${ff.letter}`, 'left');
            } else if (ff.type === 'T') {
                drawInternalPin(g, ff.pin_in1.x, ff.pin_in1.y, `T${ff.letter}`, 'left');
            }

            // Outputs Q and Q'
            drawInternalPin(g, ff.pin_out_q.x, ff.pin_out_q.y, `Q${ff.letter}`, 'right');
            drawInternalPin(g, ff.pin_out_q_bar.x, ff.pin_out_q_bar.y, `Q'${ff.letter}`, 'right', true);

            // Clock Pin on Left Edge with Negative-Edge Trigger Bubble & Triangle (Fig. 8.11 style)
            const clkStubX = ff.x - 16;
            // Vertical drop from top Clock Rail (Y = 72) down to CLK pin (Y = 215)
            svg.appendChild(createSvgPath(`M ${clkStubX} ${clkY} L ${clkStubX} ${ff.pin_clk.y} L ${ff.pin_clk.x - 7} ${ff.pin_clk.y}`, C_CLK, 2));
            svg.appendChild(createSolderDot(clkStubX, clkY, C_CLK, 4));

            // Falling-edge trigger circle bubble
            const clkBubble = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            clkBubble.setAttribute('cx', ff.pin_clk.x - 4);
            clkBubble.setAttribute('cy', ff.pin_clk.y);
            clkBubble.setAttribute('r', '3.5');
            clkBubble.setAttribute('fill', C_FF_BG);
            clkBubble.setAttribute('stroke', C_CLK);
            clkBubble.setAttribute('stroke-width', '1.8');
            g.appendChild(clkBubble);

            // Dynamic clock triangle inside box pointing right
            const tri = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
            tri.setAttribute('points', `${ff.pin_clk.x},${ff.pin_clk.y - 7} ${ff.pin_clk.x + 9},${ff.pin_clk.y} ${ff.pin_clk.x},${ff.pin_clk.y + 7}`);
            tri.setAttribute('fill', 'none');
            tri.setAttribute('stroke', C_CLK);
            tri.setAttribute('stroke-width', '1.8');
            g.appendChild(tri);

            // Output Lead Wire with Upward Arrow Probe (Fig. 8.11 hallmark!)
            g.appendChild(createSvgPath(`M ${ff.pin_out_q.x} ${ff.pin_out_q.y} L ${ff.probe_x} ${ff.pin_out_q.y}`, C_PROBE, 2.2));
            g.appendChild(createSolderDot(ff.probe_x, ff.pin_out_q.y, C_PROBE, 4));

            // Vertical probe line shooting straight UP
            const probeLine = createSvgPath(`M ${ff.probe_x} ${ff.pin_out_q.y} L ${ff.probe_x} 36`, C_PROBE, 2.2);
            probeLine.setAttribute('marker-end', 'url(#arrow-up)');
            g.appendChild(probeLine);

            // Probe text label: "QA(LSB)", "QB", "QC", "QD(MSB)"
            const probeLabel = ff.isLsb ? `QA(LSB)` : (ff.isMsb ? `Q${ff.letter}(MSB)` : `Q${ff.letter}`);
            g.appendChild(createSvgText(ff.probe_x, 20, probeLabel, C_PROBE, '13px', '800', 'middle'));

            svg.appendChild(g);
        });

        // --- Circuit Interconnections & Logic Gates ---
        const equations = currentDesign ? currentDesign.step7_kmaps_and_equations.equations : {};

        // Detect Standard Up Counter vs Standard Down Counter vs General
        const isUpCounter = checkIfStandardUpCounter(equations, ffCount);
        const isDownCounter = checkIfStandardDownCounter(equations, ffCount);

        if (isUpCounter) {
            renderExactFig811UpCounter(svg, ffLayout, ffList, C_WIRE, C_AND, C_VCC);
        } else if (isDownCounter) {
            renderExactFig813DownCounter(svg, ffLayout, ffList, C_WIRE, C_AND, C_VCC);
        } else {
            renderGeneralConnectedCircuit(svg, ffLayout, ffList, equations, C_WIRE, C_AND, C_OR, C_VCC, C_GND);
        }
    }

    function checkIfStandardUpCounter(equations, ffCount) {
        const hasJA = (equations['JA'] && equations['JA'].sop === '1') || (equations['TA'] && equations['TA'].sop === '1');
        const hasJB = (equations['JB'] && equations['JB'].sop === 'QA') || (equations['TB'] && equations['TB'].sop === 'QA');
        if (!hasJA || !hasJB) return false;
        if (ffCount >= 3) {
            const hasJC = (equations['JC'] && (equations['JC'].sop === 'QAQB' || equations['JC'].sop === 'QBQA')) || (equations['TC'] && (equations['TC'].sop === 'QAQB' || equations['TC'].sop === 'QBQA'));
            if (!hasJC) return false;
        }
        return true;
    }

    function checkIfStandardDownCounter(equations, ffCount) {
        const hasJA = (equations['JA'] && equations['JA'].sop === '1') || (equations['TA'] && equations['TA'].sop === '1');
        const hasJB = (equations['JB'] && equations['JB'].sop.includes("QA'")) || (equations['TB'] && equations['TB'].sop.includes("QA'"));
        if (!hasJA || !hasJB) return false;
        if (ffCount >= 3) {
            const hasJC = (equations['JC'] && equations['JC'].sop.includes("QA'") && equations['JC'].sop.includes("QB'")) || (equations['TC'] && equations['TC'].sop.includes("QA'") && equations['TC'].sop.includes("QB'"));
            if (!hasJC) return false;
        }
        return true;
    }

    // --- Fig. 8.11: 4-Bit / 3-Bit Synchronous Counter (Textbook Exact Layout) ---
    function renderExactFig811UpCounter(svg, ffLayout, ffList, C_WIRE, C_AND, C_VCC) {
        const ffA = ffLayout['QA'];
        const ffB = ffLayout['QB'];
        const ffC = ffLayout['QC'];
        const ffD = ffLayout['QD'];
        const ffCount = ffList.length;

        // 1. VCC (+5V / Logic 1) connected to Flip-flop A (JA and KA tied together)
        const jumperAX = ffA.x - 26;
        svg.appendChild(createSvgPath(`M ${ffA.pin_in1.x} ${ffA.pin_in1.y} L ${jumperAX} ${ffA.pin_in1.y} L ${jumperAX} ${ffA.pin_in2.y} L ${ffA.pin_in2.x} ${ffA.pin_in2.y}`, C_VCC, 2.2));
        svg.appendChild(createSvgPath(`M 85 112 L ${jumperAX} 112 L ${jumperAX} ${ffA.pin_in1.y}`, C_VCC, 2.4));
        svg.appendChild(createSolderDot(jumperAX, 112, C_VCC, 4));

        // 2. QA output connects directly to Flip-flop B (JB and KB tied together)
        const jumperBX = ffB.x - 26;
        svg.appendChild(createSvgPath(`M ${ffB.pin_in1.x} ${ffB.pin_in1.y} L ${jumperBX} ${ffB.pin_in1.y} L ${jumperBX} ${ffB.pin_in2.y} L ${ffB.pin_in2.x} ${ffB.pin_in2.y}`, C_WIRE, 2.2));
        svg.appendChild(createSvgPath(`M ${ffA.probe_x} ${ffA.pin_out_q.y} L ${jumperBX} ${ffB.pin_in1.y}`, C_WIRE, 2.4));
        svg.appendChild(createSolderDot(jumperBX, ffB.pin_in1.y, C_WIRE, 4));

        // 3. QA Bottom Trunk Line (at Y = 470) feeding AND gates below
        const qaDropX = ffA.probe_x + 12;
        const busQaY = 470;
        const endBusX = ffD ? ffD.x - 10 : (ffC ? ffC.x - 10 : ffB.x + 80);
        svg.appendChild(createSvgPath(`M ${qaDropX} ${ffA.pin_out_q.y} L ${qaDropX} ${busQaY} L ${endBusX} ${busQaY}`, C_WIRE, 2.2));
        svg.appendChild(createSolderDot(qaDropX, ffA.pin_out_q.y, C_WIRE, 4));

        // 4. AND Gate 1 (2-input AND: QA · QB) located BELOW between FF B and FF C
        if (ffC) {
            const jumperCX = ffC.x - 26;
            svg.appendChild(createSvgPath(`M ${ffC.pin_in1.x} ${ffC.pin_in1.y} L ${jumperCX} ${ffC.pin_in1.y} L ${jumperCX} ${ffC.pin_in2.y} L ${ffC.pin_in2.x} ${ffC.pin_in2.y}`, C_WIRE, 2.2));

            const and1W = 46, and1H = 36;
            const and1X = (ffB.x + ffB.w + ffC.x) / 2 - and1W / 2;
            const and1Y = 350;

            drawIeeeAndGate(svg, and1X, and1Y, and1W, and1H, 'AND', 2);

            // Input 1 to AND 1 (from QB output dropping down)
            const tap1X = and1X - 12;
            svg.appendChild(createSvgPath(`M ${ffB.probe_x} ${ffB.pin_out_q.y} L ${tap1X} ${ffB.pin_out_q.y} L ${tap1X} ${and1Y + 9} L ${and1X - 8} ${and1Y + 9}`, C_WIRE, 2));
            svg.appendChild(createSolderDot(ffB.probe_x, ffB.pin_out_q.y, C_WIRE, 4));

            // Input 2 to AND 1 (rising from QA bottom bus at Y = 470)
            svg.appendChild(createSvgPath(`M ${tap1X} ${busQaY} L ${tap1X} ${and1Y + and1H - 9} L ${and1X - 8} ${and1Y + and1H - 9}`, C_WIRE, 2));
            svg.appendChild(createSolderDot(tap1X, busQaY, C_WIRE, 4));

            // Output of AND 1 rises up into FF C jumper (JC/KC)
            const midCY = (ffC.pin_in1.y + ffC.pin_in2.y) / 2;
            svg.appendChild(createSvgPath(`M ${and1X + and1W + 8} ${and1Y + and1H / 2} L ${jumperCX} ${and1Y + and1H / 2} L ${jumperCX} ${midCY}`, C_WIRE, 2.4));
            svg.appendChild(createSolderDot(jumperCX, midCY, C_WIRE, 4));

            // 5. AND Gate 2 (3-input AND: QA · QB · QC) located BELOW between FF C and FF D
            if (ffD) {
                const jumperDX = ffD.x - 26;
                svg.appendChild(createSvgPath(`M ${ffD.pin_in1.x} ${ffD.pin_in1.y} L ${jumperDX} ${ffD.pin_in1.y} L ${jumperDX} ${ffD.pin_in2.y} L ${ffD.pin_in2.x} ${ffD.pin_in2.y}`, C_WIRE, 2.2));

                const and2W = 50, and2H = 42;
                const and2X = (ffC.x + ffC.w + ffD.x) / 2 - and2W / 2;
                const and2Y = 415; // lower bottom position matching Fig. 8.11!

                drawIeeeAndGate(svg, and2X, and2Y, and2W, and2H, 'AND', 3);

                // Input 1 (top): drops from QC output
                const tap2X = and2X - 14;
                svg.appendChild(createSvgPath(`M ${ffC.probe_x} ${ffC.pin_out_q.y} L ${tap2X} ${ffC.pin_out_q.y} L ${tap2X} ${and2Y + 8} L ${and2X - 8} ${and2Y + 8}`, C_WIRE, 1.8));
                svg.appendChild(createSolderDot(ffC.probe_x, ffC.pin_out_q.y, C_WIRE, 4));

                // Input 2 (middle): tapped from QB line
                svg.appendChild(createSvgPath(`M ${tap1X} 390 L ${tap2X} 390 L ${tap2X} ${and2Y + 21} L ${and2X - 8} ${and2Y + 21}`, C_WIRE, 1.8));
                svg.appendChild(createSolderDot(tap1X, 390, C_WIRE, 3.5));

                // Input 3 (bottom): rises from QA bottom bus
                svg.appendChild(createSvgPath(`M ${tap2X} ${busQaY} L ${tap2X} ${and2Y + and2H - 8} L ${and2X - 8} ${and2Y + and2H - 8}`, C_WIRE, 1.8));
                svg.appendChild(createSolderDot(tap2X, busQaY, C_WIRE, 4));

                // Output of AND 2 rises up into FF D jumper (JD/KD)
                const midDY = (ffD.pin_in1.y + ffD.pin_in2.y) / 2;
                svg.appendChild(createSvgPath(`M ${and2X + and2W + 8} ${and2Y + and2H / 2} L ${jumperDX} ${and2Y + and2H / 2} L ${jumperDX} ${midDY}`, C_WIRE, 2.4));
                svg.appendChild(createSolderDot(jumperDX, midDY, C_WIRE, 4));
            }
        }
    }

    // --- Fig. 8.13: 4-Bit / 3-Bit Synchronous Down Counter (Textbook Exact Layout) ---
    function renderExactFig813DownCounter(svg, ffLayout, ffList, C_WIRE, C_AND, C_VCC) {
        const ffA = ffLayout['QA'];
        const ffB = ffLayout['QB'];
        const ffC = ffLayout['QC'];
        const ffD = ffLayout['QD'];

        // 1. VCC connected to Flip-flop A (JA and KA tied together)
        const jumperAX = ffA.x - 26;
        svg.appendChild(createSvgPath(`M ${ffA.pin_in1.x} ${ffA.pin_in1.y} L ${jumperAX} ${ffA.pin_in1.y} L ${jumperAX} ${ffA.pin_in2.y} L ${ffA.pin_in2.x} ${ffA.pin_in2.y}`, C_VCC, 2.2));
        svg.appendChild(createSvgPath(`M 85 112 L ${jumperAX} 112 L ${jumperAX} ${ffA.pin_in1.y}`, C_VCC, 2.4));
        svg.appendChild(createSolderDot(jumperAX, 112, C_VCC, 4));

        // 2. QA' output connects directly to Flip-flop B (JB and KB tied together)
        const jumperBX = ffB.x - 26;
        svg.appendChild(createSvgPath(`M ${ffB.pin_in1.x} ${ffB.pin_in1.y} L ${jumperBX} ${ffB.pin_in1.y} L ${jumperBX} ${ffB.pin_in2.y} L ${ffB.pin_in2.x} ${ffB.pin_in2.y}`, C_WIRE, 2.2));
        svg.appendChild(createSvgPath(`M ${ffA.pin_out_q_bar.x} ${ffA.pin_out_q_bar.y} L ${jumperBX} ${ffB.pin_in2.y}`, C_WIRE, 2.4));
        svg.appendChild(createSolderDot(jumperBX, ffB.pin_in2.y, C_WIRE, 4));

        // 3. QA' Bottom Trunk Line (at Y = 470) feeding AND gates below
        const qaBarDropX = ffA.pin_out_q_bar.x + 14;
        const busQaBarY = 470;
        const endBusX = ffD ? ffD.x - 10 : (ffC ? ffC.x - 10 : ffB.x + 80);
        svg.appendChild(createSvgPath(`M ${qaBarDropX} ${ffA.pin_out_q_bar.y} L ${qaBarDropX} ${busQaBarY} L ${endBusX} ${busQaBarY}`, C_WIRE, 2.2));
        svg.appendChild(createSolderDot(qaBarDropX, ffA.pin_out_q_bar.y, C_WIRE, 4));

        // 4. AND Gate 1 (2-input AND: QA' · QB') located BELOW between FF B and FF C
        if (ffC) {
            const jumperCX = ffC.x - 26;
            svg.appendChild(createSvgPath(`M ${ffC.pin_in1.x} ${ffC.pin_in1.y} L ${jumperCX} ${ffC.pin_in1.y} L ${jumperCX} ${ffC.pin_in2.y} L ${ffC.pin_in2.x} ${ffC.pin_in2.y}`, C_WIRE, 2.2));

            const and1W = 46, and1H = 36;
            const and1X = (ffB.x + ffB.w + ffC.x) / 2 - and1W / 2;
            const and1Y = 350;

            drawIeeeAndGate(svg, and1X, and1Y, and1W, and1H, 'AND', 2);

            // Input 1 from QB' output dropping down
            const tap1X = and1X - 12;
            svg.appendChild(createSvgPath(`M ${ffB.pin_out_q_bar.x} ${ffB.pin_out_q_bar.y} L ${tap1X} ${ffB.pin_out_q_bar.y} L ${tap1X} ${and1Y + 9} L ${and1X - 8} ${and1Y + 9}`, C_WIRE, 2));
            svg.appendChild(createSolderDot(ffB.pin_out_q_bar.x + 14, ffB.pin_out_q_bar.y, C_WIRE, 4));

            // Input 2 from QA' bottom bus
            svg.appendChild(createSvgPath(`M ${tap1X} ${busQaBarY} L ${tap1X} ${and1Y + and1H - 9} L ${and1X - 8} ${and1Y + and1H - 9}`, C_WIRE, 2));
            svg.appendChild(createSolderDot(tap1X, busQaBarY, C_WIRE, 4));

            // Output of AND 1 rises up into FF C jumper
            const midCY = (ffC.pin_in1.y + ffC.pin_in2.y) / 2;
            svg.appendChild(createSvgPath(`M ${and1X + and1W + 8} ${and1Y + and1H / 2} L ${jumperCX} ${and1Y + and1H / 2} L ${jumperCX} ${midCY}`, C_WIRE, 2.4));
            svg.appendChild(createSolderDot(jumperCX, midCY, C_WIRE, 4));

            // 5. AND Gate 2 (3-input AND: QA' · QB' · QC') located BELOW between FF C and FF D
            if (ffD) {
                const jumperDX = ffD.x - 26;
                svg.appendChild(createSvgPath(`M ${ffD.pin_in1.x} ${ffD.pin_in1.y} L ${jumperDX} ${ffD.pin_in1.y} L ${jumperDX} ${ffD.pin_in2.y} L ${ffD.pin_in2.x} ${ffD.pin_in2.y}`, C_WIRE, 2.2));

                const and2W = 50, and2H = 42;
                const and2X = (ffC.x + ffC.w + ffD.x) / 2 - and2W / 2;
                const and2Y = 415;

                drawIeeeAndGate(svg, and2X, and2Y, and2W, and2H, 'AND', 3);

                // Input 1 from QC' output
                const tap2X = and2X - 14;
                svg.appendChild(createSvgPath(`M ${ffC.pin_out_q_bar.x} ${ffC.pin_out_q_bar.y} L ${tap2X} ${ffC.pin_out_q_bar.y} L ${tap2X} ${and2Y + 8} L ${and2X - 8} ${and2Y + 8}`, C_WIRE, 1.8));
                svg.appendChild(createSolderDot(ffC.pin_out_q_bar.x + 14, ffC.pin_out_q_bar.y, C_WIRE, 4));

                // Input 2 from QB' line
                svg.appendChild(createSvgPath(`M ${tap1X} 390 L ${tap2X} 390 L ${tap2X} ${and2Y + 21} L ${and2X - 8} ${and2Y + 21}`, C_WIRE, 1.8));
                svg.appendChild(createSolderDot(tap1X, 390, C_WIRE, 3.5));

                // Input 3 from QA' bottom bus
                svg.appendChild(createSvgPath(`M ${tap2X} ${busQaBarY} L ${tap2X} ${and2Y + and2H - 8} L ${and2X - 8} ${and2Y + and2H - 8}`, C_WIRE, 1.8));
                svg.appendChild(createSolderDot(tap2X, busQaBarY, C_WIRE, 4));

                // Output of AND 2 rises up into FF D jumper
                const midDY = (ffD.pin_in1.y + ffD.pin_in2.y) / 2;
                svg.appendChild(createSvgPath(`M ${and2X + and2W + 8} ${and2Y + and2H / 2} L ${jumperDX} ${and2Y + and2H / 2} L ${jumperDX} ${midDY}`, C_WIRE, 2.4));
                svg.appendChild(createSolderDot(jumperDX, midDY, C_WIRE, 4));
            }
        }
    }

    // --- General Synthesized Circuit for Any Custom Sequence / BCD Decade (Fig. 8.15) ---
    function renderGeneralConnectedCircuit(svg, ffLayout, ffList, equations, C_WIRE, C_AND, C_OR, C_VCC, C_GND) {
        const channelsY = [350, 380, 420, 450];
        let chIdx = 0;

        Object.keys(ffLayout).forEach(varName => {
            const ff = ffLayout[varName];
            const letter = ff.letter;

            let in1 = '', in2 = '';
            if (ff.type === 'JK') { in1 = `J${letter}`; in2 = `K${letter}`; }
            else if (ff.type === 'SR') { in1 = `S${letter}`; in2 = `R${letter}`; }
            else if (ff.type === 'D') { in1 = `D${letter}`; }
            else if (ff.type === 'T') { in1 = `T${letter}`; }

            const eq1 = equations[in1] ? equations[in1].sop : '1';
            const eq2 = in2 ? (equations[in2] ? equations[in2].sop : '1') : null;
            const isShared = in2 && (eq1 === eq2);

            const jumperX = ff.x - 22;

            if (isShared) {
                const midY = (ff.pin_in1.y + ff.pin_in2.y) / 2;
                svg.appendChild(createSvgPath(`M ${ff.pin_in1.x} ${ff.pin_in1.y} L ${jumperX} ${ff.pin_in1.y} L ${jumperX} ${ff.pin_in2.y} L ${ff.pin_in2.x} ${ff.pin_in2.y}`, C_WIRE, 2.2));
                svg.appendChild(createSolderDot(jumperX, midY, C_WIRE, 4));
                routeExpressionToPoint(svg, eq1, jumperX, midY, ffLayout, channelsY[chIdx++ % channelsY.length], C_WIRE, C_AND, C_OR, C_VCC, C_GND);
            } else {
                svg.appendChild(createSvgPath(`M ${ff.pin_in1.x} ${ff.pin_in1.y} L ${jumperX} ${ff.pin_in1.y}`, C_WIRE, 2));
                routeExpressionToPoint(svg, eq1, jumperX, ff.pin_in1.y, ffLayout, channelsY[chIdx++ % channelsY.length], C_WIRE, C_AND, C_OR, C_VCC, C_GND);

                if (in2) {
                    svg.appendChild(createSvgPath(`M ${ff.pin_in2.x} ${ff.pin_in2.y} L ${jumperX} ${ff.pin_in2.y}`, C_WIRE, 2));
                    routeExpressionToPoint(svg, eq2, jumperX, ff.pin_in2.y, ffLayout, channelsY[chIdx++ % channelsY.length], C_WIRE, C_AND, C_OR, C_VCC, C_GND);
                }
            }
        });
    }

    function routeExpressionToPoint(svg, expr, targetX, targetY, ffLayout, chY, C_WIRE, C_AND, C_OR, C_VCC, C_GND) {
        if (expr === '1') {
            svg.appendChild(createSvgPath(`M ${targetX} ${targetY} L ${targetX - 25} ${targetY}`, C_VCC, 2.2));
            svg.appendChild(createSolderDot(targetX - 25, targetY, C_VCC, 4));
            svg.appendChild(createSvgText(targetX - 30, targetY - 6, 'HIGH (+5V)', C_VCC, '10px', '700', 'end'));
            return;
        }
        if (expr === '0') {
            svg.appendChild(createSvgPath(`M ${targetX} ${targetY} L ${targetX - 25} ${targetY}`, C_GND, 2, '4,4'));
            svg.appendChild(createSolderDot(targetX - 25, targetY, C_GND, 3.5));
            svg.appendChild(createSvgText(targetX - 30, targetY - 6, 'GND (0V)', C_GND, '10px', '600', 'end'));
            return;
        }

        // Single literal e.g. QA or QA'
        if (/^Q[A-D]'?$/.test(expr.trim())) {
            const isInv = expr.includes("'");
            const srcVar = expr.replace("'", "").trim();
            const srcFF = ffLayout[srcVar];
            if (srcFF) {
                const srcPin = isInv ? srcFF.pin_out_q_bar : srcFF.pin_out_q;
                const tapX = srcPin.x + 18;
                svg.appendChild(createSolderDot(tapX, srcPin.y, C_WIRE, 4));
                svg.appendChild(createSvgPath(`M ${tapX} ${srcPin.y} L ${tapX} ${chY} L ${targetX} ${chY} L ${targetX} ${targetY}`, C_WIRE, 2));
                svg.appendChild(createSolderDot(targetX, targetY, C_WIRE, 3.5));
            }
            return;
        }

        // Multi-term SOP (contains +)
        if (expr.includes('+')) {
            const terms = expr.split('+').map(t => t.trim());
            const orW = 46, orH = 36;
            const orX = targetX - orW - 20;
            const orY = targetY - orH / 2;

            drawIeeeOrGate(svg, orX, orY, orW, orH, '+');
            svg.appendChild(createSvgPath(`M ${orX + orW} ${targetY} L ${targetX} ${targetY}`, C_WIRE, 2.2));

            terms.forEach((term, tIdx) => {
                const inY = orY + 10 + tIdx * 16;
                routeSingleTermToGate(svg, term, orX, inY, ffLayout, chY - tIdx * 14, C_WIRE, C_AND);
            });
            return;
        }

        // Single product term (e.g. QAQB or QA'QC)
        routeSingleTermToGate(svg, expr, targetX, targetY, ffLayout, chY, C_WIRE, C_AND);
    }

    function routeSingleTermToGate(svg, term, targetX, targetY, ffLayout, chY, C_WIRE, C_AND) {
        const literals = term.match(/Q[A-D]'?/g) || [];
        if (literals.length <= 1) {
            routeExpressionToPoint(svg, term, targetX, targetY, ffLayout, chY, C_WIRE, C_AND, null, '#10b981', '#64748b');
            return;
        }

        const andW = 44, andH = 34;
        const andX = Math.max(30, targetX - andW - 24);
        const andY = targetY - andH / 2;

        drawIeeeAndGate(svg, andX, andY, andW, andH, 'AND', literals.length);
        svg.appendChild(createSvgPath(`M ${andX + andW} ${targetY} L ${targetX} ${targetY}`, C_WIRE, 2.2));

        literals.forEach((lit, lIdx) => {
            const isInv = lit.includes("'");
            const srcVar = lit.replace("'", "").trim();
            const srcFF = ffLayout[srcVar];
            const inY = andY + 8 + lIdx * 16;

            if (srcFF) {
                const srcPin = isInv ? srcFF.pin_out_q_bar : srcFF.pin_out_q;
                const tapX = srcPin.x + 14 + lIdx * 10;
                svg.appendChild(createSolderDot(tapX, srcPin.y, C_WIRE, 3.5));
                svg.appendChild(createSvgPath(`M ${tapX} ${srcPin.y} L ${tapX} ${chY} L ${andX - 8} ${chY} L ${andX - 8} ${inY} L ${andX} ${inY}`, C_WIRE, 1.8));
            }
        });
    }

    // --- Standard IEEE Logic Gate SVG Shapes (Mathematical Accuracy) ---
    function drawIeeeAndGate(svg, x, y, w, h, label, numInputs = 2) {
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        const r = h / 2;
        const straightW = w - r;

        // Exact IEEE Standard Geometry: flat back, parallel lines, continuous semicircular arc
        const pathD = `
            M ${x} ${y}
            L ${x + straightW} ${y}
            A ${r} ${r} 0 0 1 ${x + straightW} ${y + h}
            L ${x} ${y + h}
            Z
        `;
        const gatePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        gatePath.setAttribute('d', pathD);
        gatePath.setAttribute('fill', '#1a102f');
        gatePath.setAttribute('stroke', '#c084fc');
        gatePath.setAttribute('stroke-width', '2.2');
        g.appendChild(gatePath);

        // Input Pin Stubs on the flat back edge
        if (numInputs === 3) {
            g.appendChild(createSvgPath(`M ${x - 8} ${y + 8} L ${x} ${y + 8}`, '#c084fc', 2));
            g.appendChild(createSvgPath(`M ${x - 8} ${y + r} L ${x} ${y + r}`, '#c084fc', 2));
            g.appendChild(createSvgPath(`M ${x - 8} ${y + h - 8} L ${x} ${y + h - 8}`, '#c084fc', 2));
        } else {
            g.appendChild(createSvgPath(`M ${x - 8} ${y + 9} L ${x} ${y + 9}`, '#c084fc', 2));
            g.appendChild(createSvgPath(`M ${x - 8} ${y + h - 9} L ${x} ${y + h - 9}`, '#c084fc', 2));
        }

        // Output Pin Stub at the exact arc front tip
        g.appendChild(createSvgPath(`M ${x + w} ${y + r} L ${x + w + 8} ${y + r}`, '#c084fc', 2.2));

        // Label inside gate
        g.appendChild(createSvgText(x + straightW * 0.48, y + r + 4, label || 'AND', '#e9d5ff', '10px', '700', 'middle'));
        svg.appendChild(g);
    }

    function drawIeeeOrGate(svg, x, y, w, h, label) {
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        const halfH = h / 2;
        const pathD = `
            M ${x} ${y}
            Q ${x + w * 0.25} ${y + halfH} ${x} ${y + h}
            Q ${x + w * 0.6} ${y + h} ${x + w} ${y + halfH}
            Q ${x + w * 0.6} ${y} ${x} ${y}
            Z
        `;
        const gatePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        gatePath.setAttribute('d', pathD);
        gatePath.setAttribute('fill', '#261226');
        gatePath.setAttribute('stroke', '#ec4899');
        gatePath.setAttribute('stroke-width', '2.2');
        g.appendChild(gatePath);

        // Input Pin Stubs
        g.appendChild(createSvgPath(`M ${x - 8} ${y + 9} L ${x + 4} ${y + 9}`, '#ec4899', 2));
        g.appendChild(createSvgPath(`M ${x - 8} ${y + h - 9} L ${x + 4} ${y + h - 9}`, '#ec4899', 2));
        // Output Pin Stub
        g.appendChild(createSvgPath(`M ${x + w} ${y + halfH} L ${x + w + 8} ${y + halfH}`, '#ec4899', 2.2));
        // Label
        g.appendChild(createSvgText(x + w * 0.45, y + halfH + 4, label || 'OR', '#f472b6', '10px', '700', 'middle'));
        svg.appendChild(g);
    }
'''

js_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'js', 'app.js')
with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

target_start = '    // --- Step 8: Logic Circuit Schematic (Exact Textbook Standard: Fig. 8.11 & Fig. 8.13) ---'
target_end = '    // --- SVG Drawing Primitives ---'

start_idx = content.find(target_start)
end_idx = content.find(target_end)

if start_idx == -1 or end_idx == -1:
    print(f'ERROR: start={start_idx}, end={end_idx}')
else:
    new_content = content[:start_idx] + new_code + '\n\n' + content[end_idx:]
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'SUCCESS: Updated static/js/app.js (replaced bytes {start_idx} to {end_idx})')
