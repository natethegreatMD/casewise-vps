/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "../../../node_modules/@cornerstonejs/labelmap-interpolation/dist/esm/workers/interpolationWorker.js":
/*!***********************************************************************************************************!*\
  !*** ../../../node_modules/@cornerstonejs/labelmap-interpolation/dist/esm/workers/interpolationWorker.js ***!
  \***********************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var comlink__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! comlink */ "../../../node_modules/comlink/dist/esm/comlink.mjs");
/* harmony import */ var _kitware_vtk_js_Common_DataModel_ImageData__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @kitware/vtk.js/Common/DataModel/ImageData */ "../../../node_modules/@kitware/vtk.js/Common/DataModel/ImageData.js");
/* harmony import */ var _kitware_vtk_js_Common_Core_DataArray__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @kitware/vtk.js/Common/Core/DataArray */ "../../../node_modules/@kitware/vtk.js/Common/Core/DataArray.js");



async function peerImport(moduleId) {
    try {
        switch (moduleId) {
            case 'itk-wasm':
                return Promise.all(/*! import() */[__webpack_require__.e("vendors-node_modules_axios_index_js-node_modules_itk-wasm_dist_get-transferables_js-node_modu-162441"), __webpack_require__.e("vendors-node_modules_itk-wasm_dist_index_js")]).then(__webpack_require__.bind(__webpack_require__, /*! itk-wasm */ "../../../node_modules/itk-wasm/dist/index.js"));
            case '@itk-wasm/morphological-contour-interpolation':
                return Promise.all(/*! import() */[__webpack_require__.e("vendors-node_modules_axios_index_js-node_modules_itk-wasm_dist_get-transferables_js-node_modu-162441"), __webpack_require__.e("vendors-node_modules_itk-wasm_dist_index_js"), __webpack_require__.e("node_modules_itk-wasm_morphological-contour-interpolation_dist_index_js")]).then(__webpack_require__.bind(__webpack_require__, /*! @itk-wasm/morphological-contour-interpolation */ "../../../node_modules/@itk-wasm/morphological-contour-interpolation/dist/index.js"));
            default:
                throw new Error(`Unknown module ID: ${moduleId}`);
        }
    }
    catch (error) {
        console.warn(`Error importing ${moduleId}:`, error);
        return null;
    }
}
const computeWorker = {
    getITKImage: async (args) => {
        const { imageData, options } = args;
        const { imageName, scalarData } = options;
        let Image, ImageType, IntTypes, FloatTypes, PixelTypes;
        try {
            const itkModule = await peerImport('itk-wasm');
            if (!itkModule) {
                throw new Error('Module not found');
            }
            ({ Image, ImageType, IntTypes, FloatTypes, PixelTypes } = itkModule);
        }
        catch (error) {
            console.warn("Warning: 'itk-wasm' module not found. Please install it separately.");
            return null;
        }
        const dataTypesMap = {
            Int8: IntTypes.Int8,
            UInt8: IntTypes.UInt8,
            Int16: IntTypes.Int16,
            UInt16: IntTypes.UInt16,
            Int32: IntTypes.Int32,
            UInt32: IntTypes.UInt32,
            Int64: IntTypes.Int64,
            UInt64: IntTypes.UInt64,
            Float32: FloatTypes.Float32,
            Float64: FloatTypes.Float64,
        };
        const { numberOfComponents } = imageData.get('numberOfComponents');
        const dimensions = imageData.getDimensions();
        const origin = imageData.getOrigin();
        const spacing = imageData.getSpacing();
        const directionArray = imageData.getDirection();
        const direction = new Float64Array(directionArray);
        const dataType = scalarData.constructor.name
            .replace(/^Ui/, 'UI')
            .replace(/Array$/, '');
        const metadata = undefined;
        const imageType = new ImageType(dimensions.length, dataTypesMap[dataType], PixelTypes.Scalar, numberOfComponents);
        const image = new Image(imageType);
        image.name = imageName;
        image.origin = origin;
        image.spacing = spacing;
        image.direction = direction;
        image.size = dimensions;
        image.metadata = metadata;
        image.data = scalarData;
        return image;
    },
    interpolateLabelmap: async (args) => {
        const { segmentationInfo, configuration } = args;
        const { scalarData, dimensions, spacing, origin, direction } = segmentationInfo;
        let itkModule;
        try {
            itkModule = await peerImport('@itk-wasm/morphological-contour-interpolation');
            if (!itkModule) {
                throw new Error('Module not found');
            }
        }
        catch (error) {
            console.warn("Warning: '@itk-wasm/morphological-contour-interpolation' module not found. Please install it separately.");
            return { data: scalarData };
        }
        const imageData = _kitware_vtk_js_Common_DataModel_ImageData__WEBPACK_IMPORTED_MODULE_1__["default"].newInstance();
        imageData.setDimensions(dimensions);
        imageData.setOrigin(origin);
        imageData.setDirection(direction || [1, 0, 0, 0, 1, 0, 0, 0, 1]);
        imageData.setSpacing(spacing);
        const scalarArray = _kitware_vtk_js_Common_Core_DataArray__WEBPACK_IMPORTED_MODULE_2__["default"].newInstance({
            name: 'Pixels',
            numberOfComponents: 1,
            values: scalarData,
        });
        imageData.getPointData().setScalars(scalarArray);
        imageData.modified();
        try {
            const inputImage = await computeWorker.getITKImage({
                imageData,
                options: {
                    imageName: 'interpolation',
                    scalarData: scalarData,
                },
            });
            if (!inputImage) {
                throw new Error('Failed to get ITK image');
            }
            const { outputImage } = await itkModule.morphologicalContourInterpolation(inputImage, {
                ...configuration,
                webWorker: false,
            });
            const outputScalarData = outputImage.data;
            const modifiedScalarData = new Uint16Array(scalarData.length);
            modifiedScalarData.set(scalarData);
            for (let i = 0; i < outputScalarData.length; i++) {
                const newValue = outputScalarData[i];
                const originalValue = scalarData[i];
                if (newValue !== originalValue) {
                    modifiedScalarData[i] = newValue;
                }
            }
            return { data: modifiedScalarData };
        }
        catch (error) {
            console.error(error);
            console.warn('Warning: Failed to perform morphological contour interpolation');
            return { data: scalarData };
        }
    },
};
(0,comlink__WEBPACK_IMPORTED_MODULE_0__.expose)(computeWorker);


/***/ }),

/***/ "?0c00":
/*!************************!*\
  !*** crypto (ignored) ***!
  \************************/
/***/ (() => {

/* (ignored) */

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			id: moduleId,
/******/ 			loaded: false,
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		var execOptions = { id: moduleId, module: module, factory: __webpack_modules__[moduleId], require: __webpack_require__ };
/******/ 		__webpack_require__.i.forEach(function(handler) { handler(execOptions); });
/******/ 		module = execOptions.module;
/******/ 		execOptions.factory.call(module.exports, module, module.exports, execOptions.require);
/******/ 	
/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = __webpack_modules__;
/******/ 	
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = __webpack_module_cache__;
/******/ 	
/******/ 	// expose the module execution interceptor
/******/ 	__webpack_require__.i = [];
/******/ 	
/******/ 	// the startup function
/******/ 	__webpack_require__.x = () => {
/******/ 		// Load entry module and return exports
/******/ 		var __webpack_exports__ = __webpack_require__.O(undefined, ["vendors-node_modules_comlink_dist_esm_comlink_mjs","vendors-node_modules_kitware_vtk_js_Common_DataModel_ImageData_js"], () => (__webpack_require__("../../../node_modules/@cornerstonejs/labelmap-interpolation/dist/esm/workers/interpolationWorker.js")))
/******/ 		__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 		return __webpack_exports__;
/******/ 	};
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/amd define */
/******/ 	(() => {
/******/ 		__webpack_require__.amdD = function () {
/******/ 			throw new Error('define cannot be used indirect');
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/amd options */
/******/ 	(() => {
/******/ 		__webpack_require__.amdO = {};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/chunk loaded */
/******/ 	(() => {
/******/ 		var deferred = [];
/******/ 		__webpack_require__.O = (result, chunkIds, fn, priority) => {
/******/ 			if(chunkIds) {
/******/ 				priority = priority || 0;
/******/ 				for(var i = deferred.length; i > 0 && deferred[i - 1][2] > priority; i--) deferred[i] = deferred[i - 1];
/******/ 				deferred[i] = [chunkIds, fn, priority];
/******/ 				return;
/******/ 			}
/******/ 			var notFulfilled = Infinity;
/******/ 			for (var i = 0; i < deferred.length; i++) {
/******/ 				var chunkIds = deferred[i][0];
/******/ 				var fn = deferred[i][1];
/******/ 				var priority = deferred[i][2];
/******/ 				var fulfilled = true;
/******/ 				for (var j = 0; j < chunkIds.length; j++) {
/******/ 					if ((priority & 1 === 0 || notFulfilled >= priority) && Object.keys(__webpack_require__.O).every((key) => (__webpack_require__.O[key](chunkIds[j])))) {
/******/ 						chunkIds.splice(j--, 1);
/******/ 					} else {
/******/ 						fulfilled = false;
/******/ 						if(priority < notFulfilled) notFulfilled = priority;
/******/ 					}
/******/ 				}
/******/ 				if(fulfilled) {
/******/ 					deferred.splice(i--, 1)
/******/ 					var r = fn();
/******/ 					if (r !== undefined) result = r;
/******/ 				}
/******/ 			}
/******/ 			return result;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/ensure chunk */
/******/ 	(() => {
/******/ 		__webpack_require__.f = {};
/******/ 		// This file contains only the entry chunk.
/******/ 		// The chunk loading function for additional chunks
/******/ 		__webpack_require__.e = (chunkId) => {
/******/ 			return Promise.all(Object.keys(__webpack_require__.f).reduce((promises, key) => {
/******/ 				__webpack_require__.f[key](chunkId, promises);
/******/ 				return promises;
/******/ 			}, []));
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/get javascript chunk filename */
/******/ 	(() => {
/******/ 		// This function allow to reference async chunks and sibling chunks for the entrypoint
/******/ 		__webpack_require__.u = (chunkId) => {
/******/ 			// return url for filenames based on template
/******/ 			return "" + chunkId + ".js";
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/global */
/******/ 	(() => {
/******/ 		__webpack_require__.g = (function() {
/******/ 			if (typeof globalThis === 'object') return globalThis;
/******/ 			try {
/******/ 				return this || new Function('return this')();
/******/ 			} catch (e) {
/******/ 				if (typeof window === 'object') return window;
/******/ 			}
/******/ 		})();
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/node module decorator */
/******/ 	(() => {
/******/ 		__webpack_require__.nmd = (module) => {
/******/ 			module.paths = [];
/******/ 			if (!module.children) module.children = [];
/******/ 			return module;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/publicPath */
/******/ 	(() => {
/******/ 		__webpack_require__.p = "/";
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/react refresh */
/******/ 	(() => {
/******/ 		__webpack_require__.i.push((options) => {
/******/ 			const originalFactory = options.factory;
/******/ 			options.factory = function (moduleObject, moduleExports, webpackRequire) {
/******/ 				__webpack_require__.$Refresh$.setup(options.id);
/******/ 				try {
/******/ 					originalFactory.call(this, moduleObject, moduleExports, webpackRequire);
/******/ 				} finally {
/******/ 					if (typeof Promise !== 'undefined' && moduleObject.exports instanceof Promise) {
/******/ 						options.module.exports = options.module.exports.then(
/******/ 							(result) => {
/******/ 								__webpack_require__.$Refresh$.cleanup(options.id);
/******/ 								return result;
/******/ 							},
/******/ 							(reason) => {
/******/ 								__webpack_require__.$Refresh$.cleanup(options.id);
/******/ 								return Promise.reject(reason);
/******/ 							}
/******/ 						);
/******/ 					} else {
/******/ 						__webpack_require__.$Refresh$.cleanup(options.id)
/******/ 					}
/******/ 				}
/******/ 			};
/******/ 		})
/******/ 		
/******/ 		__webpack_require__.$Refresh$ = {
/******/ 			register: () => (undefined),
/******/ 			signature: () => ((type) => (type)),
/******/ 			runtime: {
/******/ 				createSignatureFunctionForTransform: () => ((type) => (type)),
/******/ 				register: () => (undefined)
/******/ 			},
/******/ 			setup: (currentModuleId) => {
/******/ 				const prevModuleId = __webpack_require__.$Refresh$.moduleId;
/******/ 				const prevRegister = __webpack_require__.$Refresh$.register;
/******/ 				const prevSignature = __webpack_require__.$Refresh$.signature;
/******/ 				const prevCleanup = __webpack_require__.$Refresh$.cleanup;
/******/ 		
/******/ 				__webpack_require__.$Refresh$.moduleId = currentModuleId;
/******/ 		
/******/ 				__webpack_require__.$Refresh$.register = (type, id) => {
/******/ 					const typeId = currentModuleId + " " + id;
/******/ 					__webpack_require__.$Refresh$.runtime.register(type, typeId);
/******/ 				}
/******/ 		
/******/ 				__webpack_require__.$Refresh$.signature = () => (__webpack_require__.$Refresh$.runtime.createSignatureFunctionForTransform());
/******/ 		
/******/ 				__webpack_require__.$Refresh$.cleanup = (cleanupModuleId) => {
/******/ 					if (currentModuleId === cleanupModuleId) {
/******/ 						__webpack_require__.$Refresh$.moduleId = prevModuleId;
/******/ 						__webpack_require__.$Refresh$.register = prevRegister;
/******/ 						__webpack_require__.$Refresh$.signature = prevSignature;
/******/ 						__webpack_require__.$Refresh$.cleanup = prevCleanup;
/******/ 					}
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/importScripts chunk loading */
/******/ 	(() => {
/******/ 		__webpack_require__.b = self.location + "";
/******/ 		
/******/ 		// object to store loaded chunks
/******/ 		// "1" means "already loaded"
/******/ 		var installedChunks = {
/******/ 			"interpolation": 1
/******/ 		};
/******/ 		
/******/ 		// importScripts chunk loading
/******/ 		var installChunk = (data) => {
/******/ 			var chunkIds = data[0];
/******/ 			var moreModules = data[1];
/******/ 			var runtime = data[2];
/******/ 			for(var moduleId in moreModules) {
/******/ 				if(__webpack_require__.o(moreModules, moduleId)) {
/******/ 					__webpack_require__.m[moduleId] = moreModules[moduleId];
/******/ 				}
/******/ 			}
/******/ 			if(runtime) runtime(__webpack_require__);
/******/ 			while(chunkIds.length)
/******/ 				installedChunks[chunkIds.pop()] = 1;
/******/ 			parentChunkLoadingFunction(data);
/******/ 		};
/******/ 		__webpack_require__.f.i = (chunkId, promises) => {
/******/ 			// "1" is the signal for "already loaded"
/******/ 			if(!installedChunks[chunkId]) {
/******/ 				if(true) { // all chunks have JS
/******/ 					importScripts(__webpack_require__.p + __webpack_require__.u(chunkId));
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 		
/******/ 		var chunkLoadingGlobal = self["webpackChunk"] = self["webpackChunk"] || [];
/******/ 		var parentChunkLoadingFunction = chunkLoadingGlobal.push.bind(chunkLoadingGlobal);
/******/ 		chunkLoadingGlobal.push = installChunk;
/******/ 		
/******/ 		// no HMR
/******/ 		
/******/ 		// no HMR manifest
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/startup chunk dependencies */
/******/ 	(() => {
/******/ 		var next = __webpack_require__.x;
/******/ 		__webpack_require__.x = () => {
/******/ 			return Promise.all([
/******/ 				__webpack_require__.e("vendors-node_modules_comlink_dist_esm_comlink_mjs"),
/******/ 				__webpack_require__.e("vendors-node_modules_kitware_vtk_js_Common_DataModel_ImageData_js")
/******/ 			]).then(next);
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// module cache are used so entry inlining is disabled
/******/ 	// run startup
/******/ 	var __webpack_exports__ = __webpack_require__.x();
/******/ 	
/******/ })()
;
//# sourceMappingURL=interpolation.js.map