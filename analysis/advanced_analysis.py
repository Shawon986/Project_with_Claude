# Advanced Analysis Module
# ========================
# Correlation, Regression, PCA/Factor, Cluster, Discriminant Analysis

import pandas as pd
import numpy as np
import json
import os
import sys
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ANALYSIS

# Monkey-patch sklearn check_array for factor_analyzer compatibility
# sklearn >= 1.7 renamed force_all_finite → ensure_all_finite
# Must patch ALL references: the module attribute AND any direct imports
import sklearn.utils.validation as _skval
import sklearn.utils as _skutils
_original_check_array = _skval.check_array
def _patched_check_array(*args, **kwargs):
    if 'force_all_finite' in kwargs:
        kwargs['ensure_all_finite'] = kwargs.pop('force_all_finite')
    return _original_check_array(*args, **kwargs)
_skval.check_array = _patched_check_array
_skutils.check_array = _patched_check_array
# Also patch the function in sklearn.utils directly
import sklearn
sklearn.utils.check_array = _patched_check_array
sklearn.utils.validation.check_array = _patched_check_array

# ============================================================
# 1. CORRELATION ANALYSIS
# ============================================================

class CorrelationAnalyzer:
    """Correlation analysis between housing features and prices"""

    def __init__(self, df):
        self.df = df
        self.corr_matrix = None
        self.price_correlations = None

    def analyze(self):
        """Compute correlation matrix"""
        # Select numeric columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        # Filter out one-hot encoded district columns for cleaner results
        analysis_cols = [c for c in numeric_cols if not c.startswith("district_")]

        self.corr_matrix = self.df[analysis_cols].corr()

        # Correlations with total_price and unit_price
        price_corrs = {}
        for target in ["total_price", "unit_price"]:
            if target in self.corr_matrix.columns:
                corrs = self.corr_matrix[target].drop(target).sort_values(ascending=False)
                price_corrs[target] = {
                    "positive": [],
                    "negative": []
                }
                for col, val in corrs.items():
                    entry = {"feature": col, "correlation": round(float(val), 4)}
                    if val > 0:
                        price_corrs[target]["positive"].append(entry)
                    else:
                        price_corrs[target]["negative"].append(entry)

        self.price_correlations = price_corrs
        return {
            "correlation_matrix": self.corr_matrix.round(4).to_dict(),
            "price_correlations": price_corrs
        }

    def get_top_correlations(self, target="total_price", n=15):
        """Get top N correlations for a target variable"""
        if self.corr_matrix is None:
            self.analyze()

        if target in self.corr_matrix.columns:
            corrs = self.corr_matrix[target].drop(target).abs().sort_values(ascending=False).head(n)
            return [{"feature": k, "correlation": round(float(v), 4)} for k, v in corrs.items()]
        return []


# ============================================================
# 2. MULTIPLE REGRESSION ANALYSIS
# ============================================================

class RegressionAnalyzer:
    """Multiple regression analysis for housing price prediction"""

    def __init__(self, df):
        self.df = df
        self.models = {}
        self.results = {}

    def prepare_features(self, target="total_price"):
        """Prepare feature matrix and target vector"""
        # Select features
        feature_cols = [
            "floor_area", "rooms", "halls", "total_floors",
            "building_age", "decoration_level", "floor_type_encoded",
            "orientation_south", "near_subway", "floor_ratio",
        ]

        # Add district dummies
        district_cols = [c for c in self.df.columns if c.startswith("district_")]

        all_features = feature_cols + district_cols
        available = [c for c in all_features if c in self.df.columns]

        X = self.df[available].copy()
        y = self.df[target].copy() if target in self.df.columns else None

        # Drop rows with NaN
        if y is not None:
            mask = X.notna().all(axis=1) & y.notna()
            X = X[mask]
            y = y[mask]

        # Fill any remaining NaN with 0
        X = X.fillna(0)

        return X, y

    def run_ols(self):
        """Run Ordinary Least Squares regression"""
        try:
            import statsmodels.api as sm

            X, y = self.prepare_features("total_price")
            # Ensure all data is float64 to avoid statsmodels type issues
            X_sm = sm.add_constant(X.astype(float))
            y = y.astype(float)

            model = sm.OLS(y, X_sm).fit()
            self.models["ols_total_price"] = model

            # Extract key results
            summary = {
                "r_squared": round(float(model.rsquared), 4),
                "r_squared_adj": round(float(model.rsquared_adj), 4),
                "f_statistic": round(float(model.fvalue), 4),
                "f_pvalue": round(float(model.f_pvalue), 6),
                "aic": round(float(model.aic), 2),
                "bic": round(float(model.bic), 2),
                "n_observations": int(model.nobs),
            }

            # Significant coefficients
            coef_df = pd.DataFrame({
                "feature": model.params.index,
                "coefficient": model.params.values.round(4),
                "std_error": model.bse.values.round(4),
                "t_statistic": model.tvalues.values.round(4),
                "p_value": model.pvalues.values.round(6),
            })
            coef_df = coef_df.sort_values("p_value")
            summary["significant_features"] = coef_df[coef_df["p_value"] < 0.05].to_dict(orient="records")
            summary["all_coefficients"] = coef_df.to_dict(orient="records")

            self.results["ols_total_price"] = summary
            return summary

        except ImportError:
            print("[WARN] statsmodels not available, using sklearn LinearRegression")
            return self.run_linear_regression()

    def run_linear_regression(self):
        """Run sklearn LinearRegression as fallback"""
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import cross_val_score

        X, y = self.prepare_features("total_price")

        model = LinearRegression()
        model.fit(X, y)

        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5, scoring="r2")

        # Feature importance
        importance = pd.DataFrame({
            "feature": X.columns,
            "coefficient": model.coef_.round(4),
        }).sort_values("coefficient", key=abs, ascending=False)

        summary = {
            "r_squared": round(float(model.score(X, y)), 4),
            "cv_r2_mean": round(float(cv_scores.mean()), 4),
            "cv_r2_std": round(float(cv_scores.std()), 4),
            "intercept": round(float(model.intercept_), 4),
            "top_features": importance.head(10).to_dict(orient="records"),
            "all_coefficients": importance.to_dict(orient="records"),
        }

        self.models["lr_total_price"] = model
        self.results["lr_total_price"] = summary
        return summary

    def run_ridge(self, alpha=1.0):
        """Run Ridge regression"""
        from sklearn.linear_model import Ridge
        from sklearn.model_selection import cross_val_score

        X, y = self.prepare_features("total_price")

        model = Ridge(alpha=alpha)
        model.fit(X, y)
        cv_scores = cross_val_score(model, X, y, cv=5, scoring="r2")

        importance = pd.DataFrame({
            "feature": X.columns,
            "coefficient": model.coef_.round(4),
        }).sort_values("coefficient", key=abs, ascending=False)

        summary = {
            "alpha": alpha,
            "r_squared": round(float(model.score(X, y)), 4),
            "cv_r2_mean": round(float(cv_scores.mean()), 4),
            "cv_r2_std": round(float(cv_scores.std()), 4),
            "top_features": importance.head(10).to_dict(orient="records"),
        }

        self.models["ridge_total_price"] = model
        self.results["ridge_total_price"] = summary
        return summary

    def run_all(self):
        """Run all regression analyses"""
        print("Running regression analysis...")
        results = {}

        # OLS
        try:
            results["ols"] = self.run_ols()
        except Exception as e:
            print(f"  OLS regression failed: {e}")
            results["ols"] = {"error": str(e)}

        # Linear Regression with CV
        try:
            results["linear"] = self.run_linear_regression()
        except Exception as e:
            print(f"  Linear regression failed: {e}")
            results["linear"] = {"error": str(e)}

        # Ridge
        try:
            results["ridge"] = self.run_ridge(alpha=1.0)
        except Exception as e:
            print(f"  Ridge regression failed: {e}")
            results["ridge"] = {"error": str(e)}

        return results


# ============================================================
# 3. PCA / FACTOR ANALYSIS
# ============================================================

class FactorPCAnalyzer:
    """Principal Component Analysis and Factor Analysis"""

    def __init__(self, df):
        self.df = df
        self.pca_model = None
        self.fa_model = None
        self.pca_results = None
        self.fa_results = None

    def prepare_data(self):
        """Prepare numeric data for PCA/FA"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        exclude = [c for c in numeric_cols if c.startswith("district_")]
        feature_cols = [c for c in numeric_cols if c not in exclude]

        data = self.df[feature_cols].dropna()
        return data

    def run_pca(self, n_components=None):
        """Run Principal Component Analysis"""
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler

        data = self.prepare_data()
        X = StandardScaler().fit_transform(data)

        if n_components is None:
            n_components = min(len(data.columns), ANALYSIS["n_factors"])

        pca = PCA(n_components=n_components)
        X_pca = pca.fit_transform(X)

        # Explained variance
        explained_var = pca.explained_variance_ratio_
        cumulative_var = np.cumsum(explained_var)

        # Component loadings
        loadings = pd.DataFrame(
            pca.components_.T,
            columns=[f"PC{i+1}" for i in range(n_components)],
            index=data.columns
        )

        # Component scores (mean per component)
        scores = pd.DataFrame(
            X_pca,
            columns=[f"PC{i+1}" for i in range(n_components)]
        )

        self.pca_model = pca
        self.pca_results = {
            "n_components": n_components,
            "explained_variance_ratio": [round(float(v), 4) for v in explained_var],
            "cumulative_variance": [round(float(v), 4) for v in cumulative_var],
            "loadings": {pc: loadings[pc].round(4).to_dict() for pc in loadings.columns},
            "top_loadings": {
                pc: loadings[pc].abs().sort_values(ascending=False).head(5).round(4).to_dict()
                for pc in loadings.columns
            },
            "scores_summary": {
                "mean": scores.mean().round(4).to_dict(),
                "std": scores.std().round(4).to_dict(),
            }
        }

        # Composite score
        weights = explained_var / explained_var.sum()
        composite = np.sum(X_pca * weights, axis=1)
        self.pca_results["composite_score"] = {
            "mean": round(float(composite.mean()), 4),
            "std": round(float(composite.std()), 4),
            "min": round(float(composite.min()), 4),
            "max": round(float(composite.max()), 4),
        }

        return self.pca_results

    def run_factor_analysis(self, n_factors=None):
        """Run Factor Analysis"""
        try:
            from factor_analyzer import FactorAnalyzer
            from sklearn.preprocessing import StandardScaler

            data = self.prepare_data()
            X = StandardScaler().fit_transform(data)

            if n_factors is None:
                n_factors = ANALYSIS["n_factors"]

            # Bartlett's test
            from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity
            chi2, p_value = calculate_bartlett_sphericity(data)

            # KMO test
            from factor_analyzer.factor_analyzer import calculate_kmo
            kmo_all, kmo_model = calculate_kmo(data)

            # Factor analysis — need DataFrame for column names, convert values to float
            fa = FactorAnalyzer(n_factors=n_factors, rotation="varimax")
            fa.fit(data.astype(float))

            # Loadings
            loadings = pd.DataFrame(
                fa.loadings_,
                columns=[f"Factor{i+1}" for i in range(n_factors)],
                index=data.columns
            )

            # Variance explained
            variance = fa.get_factor_variance()

            # Factor scores
            scores = pd.DataFrame(
                fa.transform(data),
                columns=[f"Factor{i+1}" for i in range(n_factors)]
            )

            # Sanitize NaN/inf for JSON serialization
            def safe_float(v, default=None):
                try:
                    f = float(v)
                    return None if (np.isnan(f) or np.isinf(f)) else round(f, 6)
                except (ValueError, TypeError):
                    return default

            self.fa_model = fa
            self.fa_results = {
                "n_factors": n_factors,
                "bartlett_chi2": safe_float(chi2),
                "bartlett_pvalue": safe_float(p_value),
                "kmo_model": safe_float(kmo_model),
                "kmo_per_variable": {str(data.columns[i]): safe_float(v) for i, v in enumerate(kmo_all)},
                "variance_explained": [safe_float(v) for v in variance[0]],
                "cumulative_variance": [safe_float(v) for v in variance[2]],
                "loadings": {f: {k: safe_float(v) for k, v in loadings[f].round(4).to_dict().items()} for f in loadings.columns},
                "top_loadings": {
                    f: {k: safe_float(v) for k, v in loadings[f].abs().sort_values(ascending=False).head(5).round(4).to_dict().items()}
                    for f in loadings.columns
                },
                "scores_summary": {
                    "mean": scores.mean().round(4).to_dict(),
                    "std": scores.std().round(4).to_dict(),
                }
            }

            # Composite score
            weights = variance[0] / variance[0].sum()
            composite = np.sum(scores.values * weights, axis=1)
            self.fa_results["composite_score"] = {
                "mean": round(float(composite.mean()), 4),
                "std": round(float(composite.std()), 4),
                "min": round(float(composite.min()), 4),
                "max": round(float(composite.max()), 4),
            }

            return self.fa_results

        except ImportError:
            print("[WARN] factor_analyzer not available")
            self.fa_results = {"error": "factor_analyzer package not installed"}
            return self.fa_results

    def run_all(self):
        """Run both PCA and Factor Analysis"""
        print("Running PCA and Factor Analysis...")
        results = {}

        try:
            results["pca"] = self.run_pca()
        except Exception as e:
            print(f"  PCA failed: {e}")
            results["pca"] = {"error": str(e)}

        try:
            results["factor_analysis"] = self.run_factor_analysis()
        except Exception as e:
            print(f"  Factor Analysis failed: {e}")
            results["factor_analysis"] = {"error": str(e)}

        return results


# ============================================================
# 4. CLUSTER ANALYSIS
# ============================================================

class ClusterAnalyzer:
    """K-Means clustering of housing listings"""

    def __init__(self, df):
        self.df = df
        self.model = None
        self.labels = None
        self.results = None

    def prepare_features(self):
        """Prepare features for clustering"""
        feature_cols = [
            "total_price", "unit_price", "floor_area", "rooms", "halls",
            "building_age", "decoration_level", "floor_type_encoded",
            "orientation_south", "near_subway", "floor_ratio",
        ]
        # Include district dummies
        district_cols = [c for c in self.df.columns if c.startswith("district_")]

        all_features = feature_cols + district_cols
        available = [c for c in all_features if c in self.df.columns]

        X = self.df[available].copy()
        X = X.fillna(X.median())

        return X, available

    def run_kmeans(self, n_clusters=None):
        """Run K-Means clustering"""
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler

        if n_clusters is None:
            n_clusters = ANALYSIS["n_clusters"]

        X, feature_names = self.prepare_features()
        X_scaled = StandardScaler().fit_transform(X)

        # Find optimal k using elbow method
        inertias = []
        K_range = range(1, min(11, len(X) + 1))
        for k in K_range:
            km = KMeans(n_clusters=k, random_state=ANALYSIS["random_state"], n_init=10)
            km.fit(X_scaled)
            inertias.append(float(km.inertia_))

        # Run with selected k
        km = KMeans(n_clusters=n_clusters, random_state=ANALYSIS["random_state"], n_init=10)
        labels = km.fit_predict(X_scaled)

        self.model = km
        self.labels = labels

        # Analyze each cluster
        df_labeled = self.df.copy()
        df_labeled["cluster"] = labels

        cluster_profiles = []
        for i in range(n_clusters):
            cluster_df = df_labeled[df_labeled["cluster"] == i]

            profile = {
                "cluster_id": int(i),
                "size": int(len(cluster_df)),
                "pct": round(float(len(cluster_df) / len(df_labeled) * 100), 1),
                "avg_total_price": round(float(cluster_df["total_price"].mean()), 2),
                "avg_unit_price": round(float(cluster_df["unit_price"].mean()), 2) if "unit_price" in cluster_df.columns else None,
                "avg_area": round(float(cluster_df["floor_area"].mean()), 2) if "floor_area" in cluster_df.columns else None,
                "avg_building_age": round(float(cluster_df["building_age"].mean()), 2) if "building_age" in cluster_df.columns else None,
                "avg_rooms": round(float(cluster_df["rooms"].mean()), 2) if "rooms" in cluster_df.columns else None,
            }

            # Top district in cluster
            if "district" in cluster_df.columns:
                top_district = cluster_df["district"].value_counts().head(3)
                profile["top_districts"] = top_district.to_dict()

            # Top decorations
            if "decoration" in cluster_df.columns:
                top_dec = cluster_df["decoration"].value_counts().head(3)
                profile["top_decorations"] = top_dec.to_dict()

            cluster_profiles.append(profile)

        # Assign cluster labels
        cluster_labels = self._label_clusters(cluster_profiles)

        self.results = {
            "n_clusters": n_clusters,
            "inertia": float(km.inertia_),
            "inertias": inertias,
            "k_range": list(K_range),
            "cluster_profiles": cluster_profiles,
            "cluster_labels": cluster_labels,
            "centroids": km.cluster_centers_.tolist(),
        }

        return self.results

    def _label_clusters(self, profiles):
        """Assign human-readable labels to clusters based on relative characteristics"""
        # Sort clusters by price and area to assign meaningful labels
        sorted_by_price = sorted(profiles, key=lambda p: p["avg_total_price"])
        sorted_by_area = sorted(profiles, key=lambda p: p["avg_area"])
        sorted_by_age = sorted(profiles, key=lambda p: p["avg_building_age"])

        n = len(profiles)
        labels = {}

        for p in profiles:
            cid = p["cluster_id"]
            price_rank = [x["cluster_id"] for x in sorted_by_price].index(cid)
            area_rank = [x["cluster_id"] for x in sorted_by_area].index(cid)
            age_rank = [x["cluster_id"] for x in sorted_by_age].index(cid)

            # Determine label based on relative position
            is_expensive = price_rank >= n * 0.6
            is_cheap = price_rank < n * 0.4
            is_large = area_rank >= n * 0.6
            is_small = area_rank < n * 0.4
            is_old = age_rank >= n * 0.6
            is_new = age_rank < n * 0.4

            if is_expensive and is_large:
                labels[cid] = "Premium Large Units"
            elif is_expensive and is_small:
                labels[cid] = "Premium Compact Units"
            elif is_expensive:
                labels[cid] = "High-End Upgrade"
            elif is_cheap and is_old:
                labels[cid] = "Old Community Starter"
            elif is_cheap and is_small:
                labels[cid] = "Compact Entry-Level"
            elif is_cheap:
                labels[cid] = "Budget-Friendly"
            elif is_large and is_new:
                labels[cid] = "Modern Family Home"
            elif is_old and is_small:
                labels[cid] = "Old Compact Unit"
            else:
                labels[cid] = "Standard Residential"

        return labels

    def get_labeled_data(self):
        """Return dataframe with cluster labels"""
        if self.labels is None:
            return None
        df_labeled = self.df.copy()
        df_labeled["cluster"] = self.labels
        if self.results and "cluster_labels" in self.results:
            df_labeled["cluster_label"] = df_labeled["cluster"].map(self.results["cluster_labels"])
        return df_labeled


# ============================================================
# 5. DISCRIMINANT ANALYSIS
# ============================================================

class DiscriminantAnalyzer:
    """Discriminant analysis to classify listings into categories"""

    def __init__(self, df, cluster_labels=None):
        self.df = df
        self.cluster_labels = cluster_labels
        self.model = None
        self.results = None

    def prepare_data(self):
        """Prepare data for discriminant analysis"""
        if self.cluster_labels is None:
            # Run clustering first
            cluster_analyzer = ClusterAnalyzer(self.df)
            cluster_analyzer.run_kmeans()
            labeled = cluster_analyzer.get_labeled_data()
            self.cluster_labels = labeled["cluster"] if labeled is not None and "cluster" in labeled.columns else None

        feature_cols = [
            "floor_area", "rooms", "halls", "total_floors",
            "building_age", "decoration_level", "floor_type_encoded",
            "orientation_south", "near_subway", "floor_ratio",
        ]
        district_cols = [c for c in self.df.columns if c.startswith("district_")]
        all_features = feature_cols + district_cols
        available = [c for c in all_features if c in self.df.columns]

        X = self.df[available].fillna(0)

        if self.cluster_labels is not None:
            y = self.cluster_labels.loc[X.index] if isinstance(self.cluster_labels, pd.Series) else self.cluster_labels
        else:
            y = None

        return X, y

    def run_lda(self):
        """Run Linear Discriminant Analysis"""
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
        from sklearn.model_selection import cross_val_score, train_test_split
        from sklearn.preprocessing import StandardScaler

        X, y = self.prepare_data()
        if y is None:
            return {"error": "No cluster labels available"}

        # Remove NaN from y
        mask = y.notna()
        X, y = X[mask], y[mask]

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=ANALYSIS["test_size"],
            random_state=ANALYSIS["random_state"], stratify=y if len(set(y)) > 1 else None
        )

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # LDA
        lda = LinearDiscriminantAnalysis()
        lda.fit(X_train_scaled, y_train)

        # Predictions
        y_pred = lda.predict(X_test_scaled)

        from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

        accuracy = accuracy_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)

        # Cross-validation
        X_scaled = scaler.fit_transform(X)
        cv_scores = cross_val_score(lda, X_scaled, y, cv=5)

        # Feature importance (LDA coefficients)
        importance = pd.DataFrame({
            "feature": X.columns,
            "importance": np.abs(lda.coef_[0]).round(4) if lda.coef_.shape[0] == 1 else np.abs(lda.coef_).mean(axis=0).round(4),
        }).sort_values("importance", ascending=False)

        self.model = lda
        self.results = {
            "accuracy": round(float(accuracy), 4),
            "cv_accuracy_mean": round(float(cv_scores.mean()), 4),
            "cv_accuracy_std": round(float(cv_scores.std()), 4),
            "confusion_matrix": cm.tolist(),
            "classification_report": report,
            "feature_importance": importance.head(10).to_dict(orient="records"),
            "n_features": int(X.shape[1]),
            "n_samples": int(X.shape[0]),
            "n_classes": int(len(set(y))),
        }

        return self.results

    def run_qda(self):
        """Run Quadratic Discriminant Analysis"""
        from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
        from sklearn.model_selection import cross_val_score, train_test_split
        from sklearn.preprocessing import StandardScaler

        X, y = self.prepare_data()
        if y is None:
            return {"error": "No cluster labels available"}

        mask = y.notna()
        X, y = X[mask], y[mask]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=ANALYSIS["test_size"],
            random_state=ANALYSIS["random_state"], stratify=y if len(set(y)) > 1 else None
        )

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        qda = QuadraticDiscriminantAnalysis(reg_param=0.1)
        qda.fit(X_train_scaled, y_train)
        y_pred = qda.predict(X_test_scaled)

        from sklearn.metrics import accuracy_score, classification_report

        accuracy = accuracy_score(y_test, y_pred)
        cv_scores = cross_val_score(qda, scaler.fit_transform(X), y, cv=5)

        return {
            "accuracy": round(float(accuracy), 4),
            "cv_accuracy_mean": round(float(cv_scores.mean()), 4),
            "cv_accuracy_std": round(float(cv_scores.std()), 4),
            "classification_report": classification_report(y_test, y_pred, output_dict=True),
        }

    def run_all(self):
        """Run both LDA and QDA"""
        print("Running discriminant analysis...")
        results = {}

        try:
            results["lda"] = self.run_lda()
        except Exception as e:
            print(f"  LDA failed: {e}")
            results["lda"] = {"error": str(e)}

        try:
            results["qda"] = self.run_qda()
        except Exception as e:
            print(f"  QDA failed: {e}")
            results["qda"] = {"error": str(e)}

        return results


# ============================================================
# MASTER ANALYSIS RUNNER
# ============================================================

def run_full_analysis(df_path, output_dir=None):
    """Run all analyses on cleaned data and save results"""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis", "results")
    os.makedirs(output_dir, exist_ok=True)

    print("Loading data...")
    df = pd.read_csv(df_path)
    print(f"Loaded {len(df)} records")

    all_results = {}

    # 1. Correlation
    print("\n" + "="*50)
    print("1/6: Correlation Analysis")
    corr = CorrelationAnalyzer(df)
    all_results["correlation"] = corr.analyze()

    # 2. Regression
    print("\n" + "="*50)
    print("2/6: Regression Analysis")
    reg = RegressionAnalyzer(df)
    all_results["regression"] = reg.run_all()

    # 3. PCA & Factor
    print("\n" + "="*50)
    print("3/6: PCA & Factor Analysis")
    pfa = FactorPCAnalyzer(df)
    all_results["pca_factor"] = pfa.run_all()

    # 4. Clustering
    print("\n" + "="*50)
    print("4/6: Cluster Analysis")
    cl = ClusterAnalyzer(df)
    all_results["clustering"] = cl.run_kmeans()

    # Save labeled data
    labeled = cl.get_labeled_data()
    if labeled is not None:
        labeled_path = os.path.join(output_dir, "labeled_data.csv")
        labeled.to_csv(labeled_path, index=False, encoding="utf-8-sig")
        print(f"  Labeled data saved to {labeled_path}")

    # 5. Discriminant
    print("\n" + "="*50)
    print("5/6: Discriminant Analysis")
    da = DiscriminantAnalyzer(df, labeled["cluster"] if labeled is not None and "cluster" in labeled.columns else None)
    all_results["discriminant"] = da.run_all()

    # Save results
    results_path = os.path.join(output_dir, "analysis_results.json")
    # Convert numpy types for JSON serialization
    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")
        return obj

    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=convert)

    print(f"\n{'='*50}")
    print(f"All analysis results saved to {results_path}")

    return all_results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run full housing data analysis")
    parser.add_argument("input", help="Path to cleaned data CSV")
    parser.add_argument("--output-dir", "-o", default=None, help="Output directory")
    args = parser.parse_args()

    run_full_analysis(args.input, args.output_dir)
