class JPPitLogPatternCreator {
    constructor() {
        this.patternCanvas = document.createElement('canvas');
        this.patternContext = this.patternCanvas.getContext('2d');
    }

    createPattern(soilType, patternSize=60, markerSize=4, lineWidth=1){
        // Ref: https://www.city.osaka.lg.jp/kensetsu/cmsfiles/contents/0000023/23825/5_04.pdf
        // Ref2: https://www.jice.or.jp/cms/kokudo/pdf/tech/material/dokouh21_08.pdf
        // Ref3: https://www.zenchiren.or.jp/houkoku/PDF/2-02.pdf
        const firstCategoryNameList = ["礫", "礫質土", "砂", "砂質土", "シルト", 
                                       "粘性土", "有機質土", "火山灰質粘性土", "高有機質土（腐植土）"];
        const secondCategoryNameList = ["砂質", "シルト質", "粘土質", "有機質", "火山灰質", 
                                        "玉石混り", "砂利、礫混り", "砂混り", "シルト混り", "粘土混り",
                                        "有機質土混り", "火山灰混り", "貝殻混り"];
        const thirdCategoryNameList = ["硬岩", "中硬岩", "軟岩、風化岩", "玉石", "浮石（軽石）", "シラス", 
                                       "スコリア", "火山灰", "ローム", "黒ボク", "マサ", "表土", "埋土", "廃棄物"];

        const categoryMatchedIndices = this.matchCategoryName_(soilType, firstCategoryNameList, secondCategoryNameList, thirdCategoryNameList);
        
        return this.createPatternBase_(categoryMatchedIndices, patternSize, markerSize, lineWidth);
    }

    matchCategoryName_(soilType, firstCategoryNameList, secondCategoryNameList, thirdCategoryNameList){

        // exceptional case
        if (soilType === "火山灰質粘性土"){
            return [7, -1, -1];
        }

        // perfect match
        const temp_firstCategoryMatchedIndex = firstCategoryNameList.findIndex(name => soilType === name);

        if (temp_firstCategoryMatchedIndex !== -1){
            return [temp_firstCategoryMatchedIndex, -1, -1];
        }
        else{
            // partial match
            const secondCategoryIndex = secondCategoryNameList.findIndex(name => soilType.includes(name));

            if (secondCategoryIndex !== -1){
                const firstCategoryIndex = firstCategoryNameList.findIndex(name => name === soilType.replace(secondCategoryNameList[secondCategoryIndex], ""));
                if (firstCategoryIndex !== -1){
                    return [firstCategoryIndex, secondCategoryIndex, -1];
                }
                else{
                    const thirdCategoryIndex = thirdCategoryNameList.findIndex(name => name === soilType);
                    return [-1, -1, thirdCategoryIndex];
                }
            }
            else{
                const thirdCategoryIndex = thirdCategoryNameList.findIndex(name => name === soilType);
                return [-1, -1, thirdCategoryIndex];
            }
        }
    }

    createPatternBase_(categoryMatchedIndices, patternSize, markerSize, lineWidth){
        const firstCategoryIndex = categoryMatchedIndices[0];
        const secondCategoryIndex = categoryMatchedIndices[1];
        const thirdCategoryIndex = categoryMatchedIndices[2];

        let firstPatternContext = null;
        let secondPatternContext = null;
        let thirdPatternContext = null;

        if (firstCategoryIndex !== -1){
            firstPatternContext = this.createFirstCategoryPattern_(firstCategoryIndex, patternSize, markerSize, lineWidth);
        }
        else if (secondCategoryIndex !== -1){
            secondPatternContext = this.createSecondCategoryPattern_(secondCategoryIndex, patternSize, markerSize, lineWidth);
        }
        else if (thirdCategoryIndex !== -1){
            thirdPatternContext = this.createThirdCategoryPattern_(thirdCategoryIndex, patternSize, markerSize, lineWidth);
        }

        return this.combinePatternContexts_(firstPatternContext, secondPatternContext, thirdPatternContext);
    }

    createFirstCategoryPattern_(firstCategoryIndex, patternSize, markerSize, lineWidth){
        const patternCanvas = document.createElement('canvas');
        patternCanvas.width = patternSize;
        patternCanvas.height = patternSize;
        const patternContext = patternCanvas.getContext('2d');

        // Index 0: 礫
        if (firstCategoryIndex === 0){

            patternContext.fillStyle = "#ffffff";
            patternContext.beginPath();
            patternContext.arc(patternSize / 4, patternSize * 3/ 4, markerSize, 0, Math.PI * 2, true); // Adjusted position
            patternContext.fill();
            patternContext.lineWidth = lineWidth;
            patternContext.stroke();

            patternContext.fillStyle = "#ffffff";
            patternContext.beginPath();
            patternContext.arc(patternSize * 3/ 4, patternSize / 4, markerSize, 0, Math.PI * 2, true); // Adjusted position
            patternContext.fill();
            patternContext.lineWidth = lineWidth;
            patternContext.stroke();

        }
        // Index 1: 礫質土
        else if (firstCategoryIndex === 1){

            for (let i = 0; i < 2; i++){                
                for (let j = 0; j < 2; j++){
                    patternContext.fillStyle = "#ffffff";
                    patternContext.beginPath();
                    patternContext.arc(patternSize / 4 + patternSize / 2 * i, patternSize / 4 + patternSize / 2 * j, markerSize, 0, Math.PI * 2, true); // Adjusted position
                    patternContext.fill();
                    patternContext.lineWidth = lineWidth;
                    patternContext.stroke();
                }
            }
        }
        // Index 2: 砂
        else if (firstCategoryIndex === 2){
            patternContext.fillStyle = "#000000";
            patternContext.beginPath();
            patternContext.arc(patternSize / 4, patternSize * 3/ 4, markerSize, 0, Math.PI * 2, true); // Adjusted position
            patternContext.fill();
            patternContext.lineWidth = lineWidth;
            patternContext.stroke();

            patternContext.fillStyle = "#000000";
            patternContext.beginPath();
            patternContext.arc(patternSize * 3/ 4, patternSize / 4, markerSize, 0, Math.PI * 2, true); // Adjusted position
            patternContext.fill();
            patternContext.lineWidth = lineWidth;
            patternContext.stroke();
        }
        // Index 3: 砂質土
        else if (firstCategoryIndex === 3){
            for (let i = 0; i < 2; i++){                
                for (let j = 0; j < 2; j++){
                    patternContext.fillStyle = "#000000";
                    patternContext.beginPath();
                    patternContext.arc(patternSize / 4 + patternSize / 2 * i, patternSize / 4 + patternSize / 2 * j, markerSize, 0, Math.PI * 2, true); // Adjusted position
                    patternContext.fill();
                    patternContext.lineWidth = lineWidth;
                    patternContext.stroke();
                }
            }
        }
        // Index 4: シルト
        else if (firstCategoryIndex === 4){
            for (let i = 0; i < 2; i++){                        
                for (let j = 0; j < 3; j++){
                    patternContext.fillStyle = "#000000";
                    patternContext.rect(patternSize / 6 + patternSize / 2 * i, patternSize / 6 + patternSize / 3 * j, patternSize / 3, lineWidth);
                    patternContext.fill();
                }
            }
        }
        // Index 5: 粘性土
        else if (firstCategoryIndex === 5){
            for (let j = 0; j < 3; j++){
                patternContext.fillStyle = "#000000";
                patternContext.rect(0, patternSize / 6 + patternSize / 3 * j, patternSize, lineWidth);
                patternContext.fill();
            }

        }
        // Index 6: 有機質土
        else if (firstCategoryIndex === 6){
            for (let i = 0; i < 2; i++){
                for (let j = 0; j < 3; j++){
                    for (let k = 0; k < 2; k++){
                        patternContext.fillStyle = "#000000";
                        patternContext.beginPath();
                        patternContext.moveTo(patternSize / 4 + patternSize / 2 * i - lineWidth / 2 + 2 * lineWidth * k, patternSize / 12 + patternSize / 3 * j);
                        patternContext.lineTo(patternSize / 4 + patternSize / 2 * i - lineWidth / 2 + 2 * lineWidth * k, patternSize * 3 / 12 + patternSize / 3 * j);
                        patternContext.closePath();
                        patternContext.lineWidth = lineWidth;
                        patternContext.stroke();
                    }
                }
            }
        }
        // Index 7: 火山灰質粘性土
        else if (firstCategoryIndex === 7){
     
            // bazier curve regressing 1/4 sin curve
            // (-pi/2, -1), (-pi/2 + (pi - 2), -1),(pi - (pi - 2)/2, 1), (pi/2, 1)
            for (let j = 0; j < 3; j++){
                patternContext.fillStyle = "#000000";
                patternContext.beginPath();
                patternContext.moveTo(0, patternSize / 6 + patternSize / 3 * j);
                patternContext.bezierCurveTo(patternSize / 6, patternSize / 3 * j, patternSize * 2 / 6, patternSize / 3 + patternSize / 3 *  j, patternSize * 3 / 6, patternSize / 6 + patternSize / 3 * j);
                patternContext.bezierCurveTo(patternSize * 4 / 6, patternSize / 3 * j, patternSize * 5 / 6, patternSize / 3 + patternSize / 3 * j, patternSize * 6 / 6, patternSize / 6 + patternSize / 3 * j);
                patternContext.lineWidth = lineWidth;
                patternContext.stroke();
            }

        }
        // Index 8: 高有機質土（腐植土）
        else if (firstCategoryIndex === 8){
            for (let i = 0; i < 2; i++){
                for (let j = 0; j < 2; j++){
                    patternContext.fillStyle = "#000000";

                    patternContext.beginPath();
                    patternContext.moveTo(15 + 30 * i, 15 + 30 * j); // Starting point
                    patternContext.lineTo(17.5 + 30 * i, 17.5 + 30 * j);
                    patternContext.lineTo(17.5 + 30 * i, 20 + 30 * j);
                    patternContext.lineTo(17.5 + 30 * i, 17.5 + 30 * j);
                    patternContext.lineTo(20 + 30 * i, 15 + 30 * j);
                    patternContext.lineTo(25 + 30 * i, 15 + 30 * j);
                    patternContext.stroke();
                }
            }
        }
        return patternContext.createPattern(patternCanvas, 'repeat');

    }

    createSecondCategoryPattern_(secondCategoryIndex, patternSize, markerSize){
    }

    createThirdCategoryPattern_(thirdCategoryIndex, patternSize, markerSize){
    }
    
    combinePatternContexts_(firstPatternContext, secondPatternContext, thirdPatternContext){
        if (thirdPatternContext !== null){
            return thirdPatternContext;
        }
        else if (firstPatternContext !== null && secondPatternContext !== null){
            return null;
        }
        else if (firstPatternContext !== null){
            return firstPatternContext;
        }
        else if (secondPatternContext !== null){
            return secondPatternContext;
        }
        else{
            return null;
        }
    }

    createDotPattern(color, spacing, radius) {
        const patternCanvas = document.createElement('canvas');
        patternCanvas.width = spacing;
        patternCanvas.height = spacing;
        const patternContext = patternCanvas.getContext('2d');

        // Draw the dot pattern
        patternContext.fillStyle = color;
        patternContext.beginPath();
        patternContext.arc(spacing / 2, spacing / 2, radius, 0, Math.PI * 2, true);
        patternContext.fill();

        return patternContext;
    }

    combine(patternContext1, patternContext2) {
        const size = Math.max(patternContext1.canvas.width, patternContext2.canvas.width);
        this.patternCanvas.width = size;
        this.patternCanvas.height = size;

        // Clear the canvas before drawing
        this.patternContext.clearRect(0, 0, size, size);

        // Draw the first pattern
        this.patternContext.drawImage(patternContext1.canvas, 0, 0);

        // Draw the second pattern
        this.patternContext.drawImage(patternContext2.canvas, 0, 0);

        return this.patternContext.createPattern(this.patternCanvas, 'repeat');
    }
}

